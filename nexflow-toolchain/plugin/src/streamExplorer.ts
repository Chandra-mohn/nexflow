/**
 * Nexflow Stream Explorer
 *
 * VS Code tree view for exploring Kafka topics and stream messages.
 * Integrates with nexflow stream CLI commands.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { getNexflowCommand } from './runtime';

const execAsync = promisify(exec);

// ============================================================================
// Tree Item Types
// ============================================================================

type StreamTreeItem = ClusterItem | TopicItem | MessageItem | LoadingItem | ErrorItem;

class ClusterItem extends vscode.TreeItem {
    constructor(
        public readonly name: string,
        public readonly profile: string,
        public readonly bootstrapServers: string,
        public readonly isDefault: boolean
    ) {
        super(name, vscode.TreeItemCollapsibleState.Collapsed);
        this.contextValue = 'cluster';
        this.tooltip = `${bootstrapServers}${isDefault ? ' (default)' : ''}`;
        this.iconPath = new vscode.ThemeIcon('server');
        this.description = isDefault ? '(default)' : undefined;
    }
}

class TopicItem extends vscode.TreeItem {
    constructor(
        public readonly name: string,
        public readonly cluster: ClusterItem,
        public readonly partitions?: number,
        public readonly messageCount?: number
    ) {
        super(name, vscode.TreeItemCollapsibleState.Collapsed);
        this.contextValue = 'topic';
        this.tooltip = `${partitions || '?'} partitions, ~${messageCount?.toLocaleString() || '?'} messages`;
        this.iconPath = new vscode.ThemeIcon('symbol-event');
        this.description = partitions ? `${partitions}p` : undefined;
    }
}

class MessageItem extends vscode.TreeItem {
    constructor(
        public readonly topic: TopicItem,
        public readonly offset: number,
        public readonly partition: number,
        public readonly key: string | null,
        public readonly value: any,
        public readonly timestamp?: string
    ) {
        super(`${offset}`, vscode.TreeItemCollapsibleState.None);
        this.contextValue = 'message';
        this.description = key || `p${partition}`;
        this.tooltip = timestamp ? `${timestamp}\n${JSON.stringify(value, null, 2).slice(0, 500)}` : undefined;
        this.iconPath = new vscode.ThemeIcon('mail');

        // Command to open message in viewer
        this.command = {
            command: 'nexflow.stream.viewMessage',
            title: 'View Message',
            arguments: [this]
        };
    }
}

class LoadingItem extends vscode.TreeItem {
    constructor() {
        super('Loading...', vscode.TreeItemCollapsibleState.None);
        this.iconPath = new vscode.ThemeIcon('loading~spin');
    }
}

class ErrorItem extends vscode.TreeItem {
    constructor(message: string) {
        super(message, vscode.TreeItemCollapsibleState.None);
        this.contextValue = 'error';
        this.iconPath = new vscode.ThemeIcon('error');
    }
}

// ============================================================================
// Stream Explorer Provider
// ============================================================================

export class StreamExplorerProvider implements vscode.TreeDataProvider<StreamTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<StreamTreeItem | undefined | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private clusters: ClusterItem[] = [];
    private topicsCache: Map<string, TopicItem[]> = new Map();
    private messagesCache: Map<string, MessageItem[]> = new Map();

    constructor(private workspaceRoot: string) {}

    refresh(): void {
        this.clusters = [];
        this.topicsCache.clear();
        this.messagesCache.clear();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: StreamTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: StreamTreeItem): Promise<StreamTreeItem[]> {
        if (!element) {
            // Root level - show clusters
            return this.getClusters();
        }

        if (element instanceof ClusterItem) {
            // Show topics for this cluster
            return this.getTopics(element);
        }

        if (element instanceof TopicItem) {
            // Show recent messages for this topic
            return this.getMessages(element);
        }

        return [];
    }

    private async getClusters(): Promise<StreamTreeItem[]> {
        if (this.clusters.length > 0) {
            return this.clusters;
        }

        try {
            // Try to load clusters from nexflow.toml
            const configPath = path.join(this.workspaceRoot, 'nexflow.toml');
            const clusters = await this.loadClustersFromConfig(configPath);

            if (clusters.length === 0) {
                // Add a default local cluster
                clusters.push(new ClusterItem(
                    'Local (dev)',
                    'dev',
                    'localhost:9092',
                    true
                ));
            }

            this.clusters = clusters;
            return clusters;
        } catch (error) {
            return [new ErrorItem(`Failed to load clusters: ${error}`)];
        }
    }

    private async loadClustersFromConfig(configPath: string): Promise<ClusterItem[]> {
        const clusters: ClusterItem[] = [];

        try {
            // Use nexflow CLI to get config info
            const nexflowCmd = await getNexflowCommand();
            const { stdout } = await execAsync(`${nexflowCmd} info --json`, {
                cwd: this.workspaceRoot
            });

            const info = JSON.parse(stdout);
            const kafkaProfiles = info.kafka?.profiles || {};
            const defaultProfile = info.kafka?.default_profile || 'dev';

            for (const [name, profile] of Object.entries(kafkaProfiles)) {
                const p = profile as any;
                clusters.push(new ClusterItem(
                    name,
                    name,
                    p.bootstrap_servers || 'localhost:9092',
                    name === defaultProfile
                ));
            }
        } catch (error) {
            // Config doesn't exist or failed to parse - return empty
        }

        return clusters;
    }

    private async getTopics(cluster: ClusterItem): Promise<StreamTreeItem[]> {
        const cacheKey = cluster.profile;

        if (this.topicsCache.has(cacheKey)) {
            return this.topicsCache.get(cacheKey)!;
        }

        try {
            const nexflowCmd = await getNexflowCommand();
            const { stdout } = await execAsync(
                `${nexflowCmd} stream topics --profile ${cluster.profile} --json`,
                { cwd: this.workspaceRoot }
            );

            const topicsData = JSON.parse(stdout);
            const topics = topicsData.map((t: any) => new TopicItem(
                t.name,
                cluster,
                t.partitions,
                t.message_count
            ));

            this.topicsCache.set(cacheKey, topics);
            return topics;
        } catch (error) {
            // Fallback: Return placeholder suggesting to peek a topic
            return [new ErrorItem('Run "nexflow stream peek <topic>" to inspect topics')];
        }
    }

    private async getMessages(topic: TopicItem): Promise<StreamTreeItem[]> {
        const cacheKey = `${topic.cluster.profile}:${topic.name}`;

        if (this.messagesCache.has(cacheKey)) {
            return this.messagesCache.get(cacheKey)!;
        }

        try {
            const nexflowCmd = await getNexflowCommand();
            const { stdout } = await execAsync(
                `${nexflowCmd} stream peek ${topic.name} --profile ${topic.cluster.profile} --limit 10 --format raw`,
                { cwd: this.workspaceRoot, timeout: 30000 }
            );

            const messages: MessageItem[] = [];
            const lines = stdout.trim().split('\n').filter(l => l);

            for (const line of lines) {
                try {
                    const msg = JSON.parse(line);
                    messages.push(new MessageItem(
                        topic,
                        msg.offset,
                        msg.partition,
                        msg.key,
                        msg.value,
                        msg.timestamp
                    ));
                } catch {
                    // Skip invalid lines
                }
            }

            this.messagesCache.set(cacheKey, messages);
            return messages.length > 0 ? messages : [new ErrorItem('No messages found')];
        } catch (error) {
            return [new ErrorItem(`Failed to fetch messages: ${error}`)];
        }
    }

    // Clear cache for a specific topic
    clearTopicCache(topic: TopicItem): void {
        const cacheKey = `${topic.cluster.profile}:${topic.name}`;
        this.messagesCache.delete(cacheKey);
        this._onDidChangeTreeData.fire(topic);
    }
}

// ============================================================================
// Message Viewer Panel
// ============================================================================

export class MessageViewerPanel {
    public static currentPanel: MessageViewerPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, message: MessageItem) {
        this._panel = panel;
        this._update(message);

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    public static show(message: MessageItem) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (MessageViewerPanel.currentPanel) {
            MessageViewerPanel.currentPanel._update(message);
            MessageViewerPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'nexflowMessage',
            `Message: ${message.offset}`,
            column || vscode.ViewColumn.One,
            { enableScripts: true }
        );

        MessageViewerPanel.currentPanel = new MessageViewerPanel(panel, message);
    }

    private _update(message: MessageItem) {
        this._panel.title = `Message: ${message.offset}`;
        this._panel.webview.html = this._getHtml(message);
    }

    private _getHtml(message: MessageItem): string {
        const valueJson = JSON.stringify(message.value, null, 2);

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message Viewer</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
        }
        .metadata {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 8px 16px;
            margin-bottom: 20px;
            padding: 12px;
            background: var(--vscode-textCodeBlock-background);
            border-radius: 4px;
        }
        .label {
            color: var(--vscode-descriptionForeground);
            font-weight: 500;
        }
        .value {
            font-family: var(--vscode-editor-font-family);
        }
        pre {
            background: var(--vscode-textCodeBlock-background);
            padding: 16px;
            border-radius: 4px;
            overflow: auto;
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size);
        }
        h2 {
            margin-top: 0;
            border-bottom: 1px solid var(--vscode-panel-border);
            padding-bottom: 8px;
        }
        .copy-btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 8px;
        }
        .copy-btn:hover {
            background: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <h2>Message Details</h2>

    <div class="metadata">
        <span class="label">Topic:</span>
        <span class="value">${message.topic.name}</span>

        <span class="label">Partition:</span>
        <span class="value">${message.partition}</span>

        <span class="label">Offset:</span>
        <span class="value">${message.offset}</span>

        <span class="label">Key:</span>
        <span class="value">${message.key || '(null)'}</span>

        <span class="label">Timestamp:</span>
        <span class="value">${message.timestamp || '-'}</span>
    </div>

    <h2>Value</h2>
    <pre id="value">${escapeHtml(valueJson)}</pre>
    <button class="copy-btn" onclick="copyValue()">Copy to Clipboard</button>

    <script>
        function copyValue() {
            const value = document.getElementById('value').textContent;
            navigator.clipboard.writeText(value);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>`;
    }

    public dispose() {
        MessageViewerPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const d = this._disposables.pop();
            if (d) d.dispose();
        }
    }
}

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ============================================================================
// Command Handlers
// ============================================================================

export function registerStreamCommands(context: vscode.ExtensionContext, provider: StreamExplorerProvider) {
    // Refresh stream explorer
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.refresh', () => {
            provider.refresh();
        })
    );

    // View message in panel
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.viewMessage', (message: MessageItem) => {
            MessageViewerPanel.show(message);
        })
    );

    // Peek topic (opens terminal with peek command)
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.peek', async (topic: TopicItem) => {
            const terminal = vscode.window.createTerminal('Nexflow Stream');
            const nexflowCmd = await getNexflowCommand();
            terminal.sendText(`${nexflowCmd} stream peek ${topic.name} --profile ${topic.cluster.profile} --follow`);
            terminal.show();
        })
    );

    // Decode topic
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.decode', async (topic: TopicItem) => {
            const outputPath = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file(`${topic.name}.json`),
                filters: { 'JSON': ['json'], 'YAML': ['yaml', 'yml'] }
            });

            if (outputPath) {
                const terminal = vscode.window.createTerminal('Nexflow Decode');
                const nexflowCmd = await getNexflowCommand();
                const format = outputPath.fsPath.endsWith('.yaml') || outputPath.fsPath.endsWith('.yml') ? 'yaml' : 'json';
                terminal.sendText(`${nexflowCmd} stream decode ${topic.name} --profile ${topic.cluster.profile} --to ${format} --output "${outputPath.fsPath}"`);
                terminal.show();
            }
        })
    );

    // Replay wizard
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.replay', async (topic: TopicItem) => {
            const targetTopic = await vscode.window.showInputBox({
                prompt: 'Enter target topic name',
                placeHolder: `${topic.name}-replay`
            });

            if (!targetTopic) return;

            const options = await vscode.window.showQuickPick([
                { label: 'Replay all messages', value: '' },
                { label: 'Replay with filter', value: '--filter' },
                { label: 'Dry run (preview only)', value: '--dry-run' }
            ], {
                placeHolder: 'Select replay mode'
            });

            if (!options) return;

            let filterExpr = '';
            if (options.value === '--filter') {
                filterExpr = await vscode.window.showInputBox({
                    prompt: 'Enter filter expression',
                    placeHolder: "status = 'pending' AND amount > 100"
                }) || '';
            }

            const terminal = vscode.window.createTerminal('Nexflow Replay');
            const nexflowCmd = await getNexflowCommand();
            let cmd = `${nexflowCmd} stream replay ${topic.name} ${targetTopic} --profile ${topic.cluster.profile}`;

            if (options.value === '--dry-run') {
                cmd += ' --dry-run --limit 10';
            } else if (filterExpr) {
                cmd += ` --filter "${filterExpr}"`;
            }

            terminal.sendText(cmd);
            terminal.show();
        })
    );

    // Diff topics
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.diff', async (topic: TopicItem) => {
            const otherTopic = await vscode.window.showInputBox({
                prompt: 'Enter topic to compare with',
                placeHolder: 'other-topic'
            });

            if (!otherTopic) return;

            const keyField = await vscode.window.showInputBox({
                prompt: 'Enter key field for comparison (optional)',
                placeHolder: 'order_id'
            });

            const terminal = vscode.window.createTerminal('Nexflow Diff');
            const nexflowCmd = await getNexflowCommand();
            let cmd = `${nexflowCmd} stream diff ${topic.name} ${otherTopic} --profile ${topic.cluster.profile}`;

            if (keyField) {
                cmd += ` --key ${keyField}`;
            }

            terminal.sendText(cmd);
            terminal.show();
        })
    );

    // Copy topic name
    context.subscriptions.push(
        vscode.commands.registerCommand('nexflow.stream.copyTopicName', (topic: TopicItem) => {
            vscode.env.clipboard.writeText(topic.name);
            vscode.window.showInformationMessage(`Copied: ${topic.name}`);
        })
    );
}

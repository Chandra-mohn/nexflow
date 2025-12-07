"""
POM Generator Module

Generates Maven pom.xml for compiling generated Nexflow Java code.
Includes Flink 1.18 dependencies, Voltage SDK, and other required libraries.
"""

from pathlib import Path
from typing import Optional


def generate_pom(
    group_id: str = "com.nexflow.generated",
    artifact_id: str = "nexflow-generated",
    version: str = "1.0.0-SNAPSHOT",
    flink_version: str = "1.18.1",
    java_version: str = "17",
    voltage_enabled: bool = True,
    project_name: Optional[str] = None,
) -> str:
    """
    Generate a Maven pom.xml for the generated Nexflow code.

    Args:
        group_id: Maven group ID
        artifact_id: Maven artifact ID
        version: Project version
        flink_version: Apache Flink version
        java_version: Java version (11, 17, 21)
        voltage_enabled: Include Voltage SDK dependencies
        project_name: Optional project name for display

    Returns:
        Complete pom.xml content as string
    """
    name = project_name or artifact_id

    # Voltage dependencies (if enabled)
    # Note: Voltage SDK is proprietary and must be installed from your internal repository
    voltage_deps = ""
    if voltage_enabled:
        voltage_deps = """
        <!-- Voltage SDK for PII encryption/tokenization (proprietary)
             To use: Install from your organization's internal Maven repository
             Or comment out if not using PII encryption features -->
        <!--
        <dependency>
            <groupId>com.voltage.securedata</groupId>
            <artifactId>voltage-securedata-sdk</artifactId>
            <version>7.4.0</version>
            <scope>provided</scope>
        </dependency>
        -->"""

    pom_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>{group_id}</groupId>
    <artifactId>{artifact_id}</artifactId>
    <version>{version}</version>
    <packaging>jar</packaging>

    <name>{name}</name>
    <description>Auto-generated Nexflow streaming application</description>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>{java_version}</maven.compiler.source>
        <maven.compiler.target>{java_version}</maven.compiler.target>
        <flink.version>{flink_version}</flink.version>
        <scala.binary.version>2.12</scala.binary.version>
        <log4j.version>2.20.0</log4j.version>
        <jackson.version>2.15.3</jackson.version>
    </properties>

    <dependencies>
        <!-- ============================================== -->
        <!-- Apache Flink Core Dependencies (provided)     -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-clients</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-runtime-web</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <!-- ============================================== -->
        <!-- Flink Connectors (Kafka, JDBC, etc.)          -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-connector-base</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-connector-kafka</artifactId>
            <version>3.1.0-1.18</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-connector-jdbc</artifactId>
            <version>3.1.2-1.18</version>
            <scope>provided</scope>
        </dependency>

        <!-- ============================================== -->
        <!-- Flink State Backend & Checkpointing           -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-statebackend-rocksdb</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <!-- ============================================== -->
        <!-- Flink Table API / SQL (optional)              -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-api-java-bridge</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <!-- ============================================== -->
        <!-- Serialization: Avro                           -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-avro</artifactId>
            <version>${{flink.version}}</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.avro</groupId>
            <artifactId>avro</artifactId>
            <version>1.11.3</version>
            <scope>provided</scope>
        </dependency>

        <!-- ============================================== -->
        <!-- JSON Processing: Jackson                      -->
        <!-- ============================================== -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>${{jackson.version}}</version>
        </dependency>

        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
            <version>${{jackson.version}}</version>
        </dependency>
{voltage_deps}
        <!-- ============================================== -->
        <!-- Logging                                       -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-slf4j2-impl</artifactId>
            <version>${{log4j.version}}</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-api</artifactId>
            <version>${{log4j.version}}</version>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-core</artifactId>
            <version>${{log4j.version}}</version>
            <scope>provided</scope>
        </dependency>

        <!-- ============================================== -->
        <!-- Testing                                       -->
        <!-- ============================================== -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.1</version>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-test-utils</artifactId>
            <version>${{flink.version}}</version>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <version>3.24.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Maven Compiler Plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.12.1</version>
                <configuration>
                    <source>{java_version}</source>
                    <target>{java_version}</target>
                    <compilerArgs>
                        <arg>-Xlint:all</arg>
                        <arg>-Xlint:-processing</arg>
                    </compilerArgs>
                </configuration>
            </plugin>

            <!-- Maven Shade Plugin for fat JAR -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.1</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <artifactSet>
                                <excludes>
                                    <exclude>org.apache.flink:flink-shaded-force-shading</exclude>
                                    <exclude>com.google.code.findbugs:jsr305</exclude>
                                    <exclude>org.slf4j:*</exclude>
                                    <exclude>org.apache.logging.log4j:*</exclude>
                                </excludes>
                            </artifactSet>
                            <filters>
                                <filter>
                                    <artifact>*:*</artifact>
                                    <excludes>
                                        <exclude>META-INF/*.SF</exclude>
                                        <exclude>META-INF/*.DSA</exclude>
                                        <exclude>META-INF/*.RSA</exclude>
                                    </excludes>
                                </filter>
                            </filters>
                            <transformers>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>com.nexflow.generated.FlinkApplication</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>

            <!-- Surefire for unit tests -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.3</version>
            </plugin>
        </plugins>
    </build>

    <!-- Repository for Voltage SDK (if needed) -->
    <repositories>
        <repository>
            <id>central</id>
            <url>https://repo.maven.apache.org/maven2</url>
        </repository>
    </repositories>
</project>
'''
    return pom_content


def write_pom(
    output_dir: Path,
    group_id: str = "com.nexflow.generated",
    artifact_id: str = "nexflow-generated",
    version: str = "1.0.0-SNAPSHOT",
    flink_version: str = "1.18.1",
    java_version: str = "17",
    voltage_enabled: bool = True,
    project_name: Optional[str] = None,
) -> Path:
    """
    Generate and write pom.xml to the output directory.

    Returns:
        Path to the generated pom.xml
    """
    pom_content = generate_pom(
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        flink_version=flink_version,
        java_version=java_version,
        voltage_enabled=voltage_enabled,
        project_name=project_name,
    )

    pom_path = output_dir / "pom.xml"
    pom_path.write_text(pom_content)
    return pom_path

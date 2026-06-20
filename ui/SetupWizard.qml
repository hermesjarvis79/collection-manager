/*
 * Collection Manager — Setup Wizard
 * First-run configuration dialog.
 */
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    title: "Collection Manager — Setup"
    modal: true
    width: 520
    height: 480
    closePolicy: Popup.NoAutoClose
    standardButtons: Dialog.Ok

    property string watchedFolder: ""
    property string thresholdType: "percentage"
    property real thresholdValue: 85
    property bool autoDelete: false

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 20

        Text {
            text: "WELCOME"
            color: "#00fff7"
            font.pixelSize: 24
            font.bold: true
            font.family: "Consolas, monospace"
            letterSpacing: 4
        }

        Text {
            text: "Let's configure your collection manager."
            color: "#888888"
            font.pixelSize: 13
            font.family: "Segoe UI, sans-serif"
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#222222" }

        // ── Watched Folder ──────────────────────────────────────────────
        ColumnLayout {
            spacing: 6
            Text {
                text: "WATCHED FOLDER"
                color: "#aaaaaa"
                font.pixelSize: 10
                font.family: "Consolas, monospace"
                letterSpacing: 1
            }
            RowLayout {
                TextField {
                    Layout.fillWidth: true
                    placeholderText: "C:\\Users\\...\\Movies"
                    text: watchedFolder
                    onTextChanged: watchedFolder = text
                    color: "#ffffff"
                    background: Rectangle {
                        color: "#1a1a1a"
                        border.color: "#333333"
                        border.width: 1
                        radius: 3
                    }
                }
                Button {
                    text: "Browse..."
                    onClicked: {
                        // TODO: Open folder dialog
                    }
                }
            }
        }

        // ── Storage Threshold ───────────────────────────────────────────
        ColumnLayout {
            spacing: 6
            Text {
                text: "STORAGE THRESHOLD"
                color: "#aaaaaa"
                font.pixelSize: 10
                font.family: "Consolas, monospace"
                letterSpacing: 1
            }
            RowLayout {
                ComboBox {
                    model: ["Percentage of drive", "Absolute free space (GB)]
                    currentIndex: thresholdType === "percentage" ? 0 : 1
                    onCurrentIndexChanged: {
                        thresholdType = currentIndex === 0 ? "percentage" : "absolute_gb"
                    }
                }
                SpinBox {
                    from: 1
                    to: 99
                    value: thresholdValue
                    onValueModified: thresholdValue = value
                }
                Text {
                    text: thresholdType === "percentage" ? "%" : "GB"
                    color: "#888888"
                    font.pixelSize: 14
                    font.family: "Consolas, monospace"
                }
            }
        }

        // ── Auto-Delete ─────────────────────────────────────────────────
        ColumnLayout {
            spacing: 6
            CheckBox {
                text: "Enable auto-delete"
                checked: autoDelete
                onCheckedChanged: autoDelete = checked
                contentItem: Text {
                    text: parent.text
                    color: autoDelete ? "#ff0066" : "#888888"
                    font.pixelSize: 13
                    font.family: "Segoe UI, sans-serif"
                    leftPadding: 24
                }
            }
            Text {
                text: "⚠ WARNING: When enabled, the app will automatically delete the oldest movies when the threshold is reached. This cannot be undone."
                color: autoDelete ? "#ff0066" : "#555555"
                font.pixelSize: 11
                font.family: "Segoe UI, sans-serif"
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                leftPadding: 24
                visible: autoDelete
            }
        }

        Rectangle { Layout.fillHeight: true }
    }

    onAccepted: {
        settingsBridge.setWatchedFolder(watchedFolder)
        settingsBridge.set("threshold_type", thresholdType)
        settingsBridge.set("threshold_value", String(thresholdValue))
        settingsBridge.setAutoDelete(autoDelete)
        settingsBridge.set("setup_complete", "true")
    }
}

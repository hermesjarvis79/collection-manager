/*
 * Collection Manager — Preferences Dialog
 * Allows the user to change all app settings after initial setup.
 */
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    title: "Preferences"
    modal: true
    width: 480
    height: 520
    standardButtons: Dialog.Ok | Dialog.Cancel

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        Text {
            text: "PREFERENCES"
            color: "#00fff7"
            font.pixelSize: 18
            font.bold: true
            font.family: "Consolas, monospace"
            letterSpacing: 3
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#222222" }

        // ── Watched Folder ──────────────────────────────────────────────
        ColumnLayout {
            spacing: 4
            Label { text: "Watched Folder"; color: "#aaaaaa"; font.pixelSize: 10; font.family: "Consolas, monospace" }
            RowLayout {
                TextField {
                    id: folderField
                    Layout.fillWidth: true
                    text: settingsBridge.getWatchedFolder()
                    color: "#ffffff"
                    background: Rectangle { color: "#1a1a1a"; border.color: "#333333"; border.width: 1; radius: 3 }
                }
                Button { text: "Browse..." }
            }
        }

        // ── Threshold ───────────────────────────────────────────────────
        ColumnLayout {
            spacing: 4
            Label { text: "Storage Threshold"; color: "#aaaaaa"; font.pixelSize: 10; font.family: "Consolas, monospace" }
            RowLayout {
                ComboBox {
                    id: thresholdTypeBox
                    model: ["Percentage", "Absolute GB"]
                    currentIndex: settingsBridge.getThresholdType() === "percentage" ? 0 : 1
                }
                SpinBox {
                    id: thresholdValueBox
                    from: 1
                    to: 999
                    value: settingsBridge.getThresholdValue()
                }
                Label {
                    text: settingsBridge.getThresholdType() === "percentage" ? "% full" : "GB free"
                    color: "#888888"
                    font.family: "Consolas, monospace"
                }
            }
        }

        // ── Auto-Delete ─────────────────────────────────────────────────
        ColumnLayout {
            spacing: 4
        }

        CheckBox {
            id: autoDeleteBox
            text: "Enable auto-delete"
            checked: settingsBridge.getAutoDelete()
            contentItem: Text {
                text: parent.text
                color: autoDeleteBox.checked ? "#ff0066" : "#888888"
                font.pixelSize: 13
                leftPadding: 24
            }
        }

        Text {
            text: "⚠ WARNING: Oldest movies will be automatically deleted when the storage threshold is reached. Files will be permanently removed."
            color: autoDeleteBox.checked ? "#ff0066" : "#444444"
            font.pixelSize: 11
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            leftPadding: 24
            visible: autoDeleteBox.checked
        }

        Rectangle { Layout.fillHeight: true }
    }

    onAccepted: {
        settingsBridge.setWatchedFolder(folderField.text)
        settingsBridge.set("threshold_type", thresholdTypeBox.currentIndex === 0 ? "percentage" : "absolute_gb")
        settingsBridge.set("threshold_value", String(thresholdValueBox.value))
        settingsBridge.setAutoDelete(autoDeleteBox.checked)
    }
}

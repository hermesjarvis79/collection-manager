/*
 * Collection Manager — Stats Panel (Cyberpunk HUD)
 * Displays storage statistics with a digital punk rock aesthetic.
 */
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    height: 200
    color: "#0a0a0a"
    opacity: 0.95
    radius: 4
    border.color: "#00fff7"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        // ── Header ──────────────────────────────────────────────────────
        Text {
            text: "◈ STORAGE"
            color: "#00fff7"
            font.pixelSize: 11
            font.bold: true
            font.family: "Consolas, monospace"
            letterSpacing: 2
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#1a3a3a"
        }

        // ── Stats ───────────────────────────────────────────────────────
        ColumnLayout {
            spacing: 6

            // Used / Total
            RowLayout {
                Text {
                    text: "USED"
                    color: "#666666"
                    font.pixelSize: 9
                    font.family: "Consolas, monospace"
                }
                Rectangle { Layout.fillWidth: true }
                Text {
                    text: formatSize(storageBridge.getStats().used_gb) + " / " + formatSize(storageBridge.getStats().total_gb)
                    color: "#ffffff"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                    font.bold: true
                }
            }

            // Progress bar
            Rectangle {
                Layout.fillWidth: true
                height: 6
                color: "#1a1a1a"
                radius: 3

                Rectangle {
                    width: parent.width * (storageBridge.getStats().used_percent / 100)
                    height: parent.height
                    color: storageBridge.getStats().used_percent > 85 ? "#ff0066" : "#00fff7"
                    radius: 3
                }
            }

            // Free space
            RowLayout {
                Text {
                    text: "FREE"
                    color: "#666666"
                    font.pixelSize: 9
                    font.family: "Consolas, monospace"
                }
                Rectangle { Layout.fillWidth: true }
                Text {
                    text: formatSize(storageBridge.getStats().free_gb)
                    color: storageBridge.getStats().free_gb < 20 ? "#ff0066" : "#00ff88"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                    font.bold: true
                }
            }

            // Movie count
            RowLayout {
                Text {
                    text: "MOVIES"
                    color: "#666666"
                    font.pixelSize: 9
                    font.family: "Consolas, monospace"
                }
                Rectangle { Layout.fillWidth: true }
                Text {
                    text: String(storageBridge.getStats().movie_count)
                    color: "#ffffff"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                    font.bold: true
                }
            }

            // Library size
            RowLayout {
                Text {
                    text: "LIB SIZE"
                    color: "#666666"
                    font.pixelSize: 9
                    font.family: "Consolas, monospace"
                }
                Rectangle { Layout.fillWidth: true }
                Text {
                    text: formatSize(storageBridge.getStats().library_size_gb)
                    color: "#ffffff"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                    font.bold: true
                }
            }
        }

        Rectangle { Layout.fillHeight: true }

        // ── Threshold Warning ───────────────────────────────────────────
        Text {
            text: storageBridge.isThresholdReached() ? "⚠ THRESHOLD REACHED" : "✓ WITHIN LIMITS"
            color: storageBridge.isThresholdReached() ? "#ff0066" : "#00ff88"
            font.pixelSize: 9
            font.family: "Consolas, monospace"
            font.bold: true
        }
    }

    function formatSize(gb) {
        if (gb >= 1000) return (gb / 1000).toFixed(1) + " TB"
        return gb.toFixed(1) + " GB"
    }
}

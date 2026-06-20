/*
 * Collection Manager — Main Dashboard
 * Split layout: Carousel (top) + Grid (bottom) with fluid resize
 * Cyberpunk dark theme: black background, white text, neon accents
 */
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 800
    title: "Collection Manager"
    color: "#0a0a0a"

    // ── State ──────────────────────────────────────────────────────────
    property int carouselPercent: 40  // 30, 40, 50, or 100 (fullscreen)
    property bool statsVisible: settingsBridge.get("stats_visible") === "true"
    property bool setupComplete: settingsBridge.get("setup_complete") === "true"
    property var currentMovie: null
    property var allMovies: []

    // ── Initialization ─────────────────────────────────────────────────
    Component.onCompleted: {
        allMovies = dbBridge.getAllMovies()
        if (allMovies.length > 0) {
            currentMovie = allMovies[0]
        }
        if (!setupComplete) {
            setupWizard.open()
        }
    }

    // ── Top Toolbar ────────────────────────────────────────────────────
    header: Rectangle {
        height: 48
        color: "#111111"

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            spacing: 12

            // App title
            Text {
                text: "COLLECTION MANAGER"
                color: "#ffffff"
                font.pixelSize: 16
                font.bold: true
                font.family: "Consolas, monospace"
                letterSpacing: 4
            }

            Rectangle { Layout.fillWidth: true }

            // Carousel size presets
            Text {
                text: "VIEW"
                color: "#666666"
                font.pixelSize: 10
                font.family: "Consolas, monospace"
            }

            Repeater {
                model: [
                    { label: "30%", value: 30 },
                    { label: "40%", value: 40 },
                    { label: "50%", value: 50 },
                    { label: "FULL", value: 100 }
                ]
                Button {
                    text: modelData.label
                    flat: true
                    contentItem: Text {
                        text: parent.text
                        color: carouselPercent === modelData.value ? "#00fff7" : "#888888"
                        font.pixelSize: 12
                        font.family: "Consolas, monospace"
                        font.bold: carouselPercent === modelData.value
                    }
                    background: Rectangle {
                        color: "transparent"
                        border.color: carouselPercent === modelData.value ? "#00fff7" : "transparent"
                        border.width: 1
                    }
                    onClicked: carouselPercent = modelData.value
                }
            }

            Rectangle {
                width: 1
                height: 24
                color: "#333336"
            }

            // Stats toggle
            Button {
                text: statsVisible ? "STATS ON" : "STATS OFF"
                flat: true
                contentItem: Text {
                    text: parent.text
                    color: statsVisible ? "#00fff7" : "#666666"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                }
                background: Rectangle { color: "transparent" }
                onClicked: {
                    statsVisible = !statsVisible
                    settingsBridge.set("stats_visible", statsVisible ? "true" : "false")
                }
            }

            // Preferences
            Button {
                text: "⚙"
                flat: true
                contentItem: Text {
                    text: parent.text
                    color: "#888888"
                    font.pixelSize: 16
                }
                background: Rectangle { color: "transparent" }
                onClicked: preferencesDialog.open()
            }
        }
    }

    // ── Main Content Area ──────────────────────────────────────────────
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Carousel Stage ──────────────────────────────────────────────
        Rectangle {
            id: carouselArea
            Layout.fillWidth: true
            Layout.preferredHeight: carouselPercent === 100 ? (parent.height - 48) : (parent.height - 48) * (carouselPercent / 100)
            color: "#0a0a0a"
            visible: carouselPercent < 100 || gridArea.visible

            Carousel {
                id: carousel
                anchors.fill: parent
                movie: currentMovie
            }

            // Fullscreen toggle overlay (when in fullscreen mode)
            Rectangle {
                visible: carouselPercent === 100
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 16
                width: 40
                height: 40
                color: "#1a1a1a"
                radius: 4
                border.color: "#333333"

                Text {
                    anchors.centerIn: parent
                    text: "✕"
                    color: "#888888"
                    font.pixelSize: 18
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: carouselPercent = 40
                }
            }
        }

        // ── Resize Handle ───────────────────────────────────────────────
        Rectangle {
            id: resizeHandle
            Layout.fillWidth: true
            height: 4
            color: "#1a1a1a"
            visible: carouselPercent < 100

            Rectangle {
                anchors.centerIn: parent
                width: 60
                height: 2
                color: "#333333"
                radius: 1
            }

            MouseArea {
                anchors.fill: parent
                anchors.margins: -4
                cursorShape: Qt.SizeVerCursor
                onPressed: resizeHandle.color = "#00fff7"
                onReleased: resizeHandle.color = "#1a1a1a"
                onMouseYChanged: {
                    if (pressed) {
                        var totalH = carouselArea.parent.height - 48
                        var pct = (mouseY + carouselArea.y) / totalH * 100
                        if (pct < 20) pct = 20
                        if (pct > 95) pct = 95
                        carouselPercent = Math.round(pct)
                    }
                }
            }
        }

        // ── Grid View ───────────────────────────────────────────────────
        Rectangle {
            id: gridArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#050505"
            visible: carouselPercent < 100

            GridView {
                id: grid
                anchors.fill: parent
                anchors.margins: 12
                cellWidth: 160
                cellHeight: 260
                model: allMovies
                delegate: MovieCard {
                    movie: modelData
                    selected: currentMovie && currentMovie.id === modelData.id
                    onClicked: {
                        currentMovie = modelData
                    }
                }
                clip: true
            }
        }
    }

    // ── Stats Panel (overlay) ──────────────────────────────────────────
    StatsPanel {
        id: statsPanel
        visible: statsVisible
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 56
        anchors.rightMargin: 16
        width: 220
    }

    // ── Setup Wizard ───────────────────────────────────────────────────
    SetupWizard {
        id: setupWizard
    }

    // ── Preferences Dialog ─────────────────────────────────────────────
    PreferencesDialog {
        id: preferencesDialog
    }
}

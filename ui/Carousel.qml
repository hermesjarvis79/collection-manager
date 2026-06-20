/*
 * Collection Manager — Carousel Stage
 * Displays the selected movie with cinematic lighting effects.
 * Full-color cover art with spotlight and ambient glow.
 * Compatible with Qt6 / PyQt6 — no Qt5Compat dependencies.
 */
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#0a0a0a"

    property var movie: null

    // Spotlight color derived from movie (default cyan)
    property real spotColorR: 0.0
    property real spotColorG: 1.0
    property real spotColorB: 1.0
    property color spotlightColor: "#00fff7"

    onMovieChanged: {
        updateSpotlight()
    }

    function updateSpotlight() {
        if (movie) {
            var colors = [
                [0.0, 1.0, 1.0],   // cyan
                [1.0, 0.0, 0.67],  // magenta
                [0.0, 0.4, 1.0],   // electric blue
                [0.0, 1.0, 0.5],   // green
                [1.0, 0.6, 0.0],   // amber
            ]
            var idx = movie.id ? movie.id % colors.length : 0
            spotColorR = colors[idx][0]
            spotColorG = colors[idx][1]
            spotColorB = colors[idx][2]
            spotlightColor = Qt.rgba(spotColorR, spotColorG, spotColorB, 0.15)
        }
    }

    // ── Cinematic Background Glow (simulated with layered rectangles) ──────
    Rectangle {
        anchors.centerIn: parent
        width: parent.width * 0.7
        height: parent.height * 0.8
        radius: width / 2
        color: spotlightColor
        opacity: 0.3
    }

    Rectangle {
        anchors.centerIn: parent
        width: parent.width * 0.4
        height: parent.height * 0.5
        radius: width / 2
        color: spotlightColor
        opacity: 0.2
    }

    // ── Content Layout ─────────────────────────────────────────────────
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 32
        anchors.rightMargin: 32
        anchors.topMargin: 16
        anchors.bottomMargin: 16
        spacing: 32

        // ── Cover Art ───────────────────────────────────────────────────
        Rectangle {
            Layout.preferredWidth: parent.height * 0.65
            Layout.preferredHeight: parent.height * 0.95
            Layout.alignment: Qt.AlignVCenter
            color: "transparent"
            clip: true
            radius: 6

            // Cover image
            Image {
                id: coverImage
                anchors.fill: parent
                source: movie && movie.cover_art_path ? "file:///" + movie.cover_art_path : ""
                fillMode: Image.PreserveAspectFit
                smooth: true
                mipmap: true
                asynchronous: true

                onStatusChanged: {
                    if (status === Image.Ready) {
                        coverPlaceholder.visible = false
                    }
                }
            }

            // Placeholder when no cover
            Rectangle {
                id: coverPlaceholder
                anchors.fill: parent
                color: "#1a1a1a"
                radius: 6
                border.color: "#333333"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: movie ? movie.title.charAt(0).toUpperCase() : "?"
                    color: "#444444"
                    font.pixelSize: 48
                    font.bold: true
                }
            }

            // Glow border behind cover (simulated)
            Rectangle {
                anchors.fill: parent
                anchors.margins: -3
                color: "transparent"
                border.color: spotlightColor
                border.width: 2
                radius: 8
                opacity: 0.4
                visible: coverImage.status === Image.Ready
                z: -1
            }

            // Subtle border
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                border.color: "#222222"
                border.width: 1
                radius: 6
            }
        }

        // ── Movie Info Panel ────────────────────────────────────────────
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 12

            // Title
            Text {
                text: movie ? movie.title : "Select a Movie"
                color: "#ffffff"
                font.pixelSize: 28
                font.bold: true
                font.family: "Segoe UI, sans-serif"
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            // Year • Genre • Runtime
            Row {
                spacing: 12
                Text {
                    text: movie ? (movie.year || "") : ""
                    color: "#00fff7"
                    font.pixelSize: 14
                    font.family: "Consolas, monospace"
                }
                Text {
                    text: movie ? "•" : ""
                    color: "#444444"
                    font.pixelSize: 14
                }
                Text {
                    text: movie ? (movie.genre || "") : ""
                    color: "#888888"
                    font.pixelSize: 14
                    font.family: "Consolas, monospace"
                }
                Text {
                    text: movie ? "•" : ""
                    color: "#444444"
                    font.pixelSize: 14
                }
                Text {
                    text: movie ? (movie.runtime_minutes ? movie.runtime_minutes + " min" : "") : ""
                    color: "#888888"
                    font.pixelSize: 14
                    font.family: "Consolas, monospace"
                }
            }

            // Rating
            Row {
                spacing: 6
                Text {
                    text: movie ? (movie.rating ? "★ " + movie.rating.toFixed(1) : "") : ""
                    color: "#ffaa00"
                    font.pixelSize: 16
                    font.bold: true
                    font.family: "Consolas, monospace"
                }
                Text {
                    text: movie ? (movie.imdb_id ? "IMDb" : "") : ""
                    color: "#666666"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                }
            }

            // Director
            Text {
                text: movie && movie.director ? "Directed by " + movie.director : ""
                color: "#aaaaaa"
                font.pixelSize: 13
                font.family: "Segoe UI, sans-serif"
            }

            // Cast
            Text {
                text: movie && movie.cast ? "Starring: " + movie.cast : ""
                color: "#888888"
                font.pixelSize: 12
                font.family: "Segoe UI, sans-serif"
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            // Synopsis
            Text {
                text: movie ? (movie.synopsis || "") : ""
                color: "#777777"
                font.pixelSize: 13
                font.family: "Segoe UI, sans-serif"
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                Layout.maximumHeight: 120
                elide: Text.ElideRight
                lineHeight: 1.4
            }

            Rectangle { Layout.fillHeight: true }

            // ── File Info ────────────────────────────────────────────────
            Row {
                spacing: 16
                Text {
                    text: movie ? "Size: " + formatSize(movie.file_size_bytes) : ""
                    color: "#555555"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                }
                Text {
                    text: movie ? "Added: " + formatDate(movie.date_added) : ""
                    color: "#555555"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                }
            }

            // ── Trailer Button ───────────────────────────────────────────
            Button {
                text: "▶  PLAY TRAILER"
                visible: movie && movie.trailer_youtube_key
                flat: true
                contentItem: Text {
                    text: parent.text
                    color: "#00fff7"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Consolas, monospace"
                }
                background: Rectangle {
                    color: "transparent"
                    border.color: "#00fff7"
                    border.width: 1
                    radius: 4
                }
                onClicked: {
                    if (movie && movie.trailer_youtube_key) {
                        vlcBridge.playTrailer("https://www.youtube.com/watch?v=" + movie.trailer_youtube_key)
                    }
                }
            }
        }
    }

    // ── Helper Functions ───────────────────────────────────────────────
    function formatSize(bytes) {
        if (!bytes) return "—"
        var gb = bytes / (1024 * 1024 * 1024)
        if (gb >= 1) return gb.toFixed(1) + " GB"
        var mb = bytes / (1024 * 1024)
        return mb.toFixed(0) + " MB"
    }

    function formatDate(dateStr) {
        if (!dateStr) return "—"
        var d = new Date(dateStr)
        if (isNaN(d.getTime())) return dateStr
        return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
    }
}

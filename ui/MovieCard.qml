/*
 * Collection Manager — Movie Card (Grid Item)
 * Displays a single movie as a cover art thumbnail with info overlay.
 */
import QtQuick

Rectangle {
    id: root
    width: 148
    height: 240
    color: "transparent"
    radius: 4

    property var movie: null
    property bool selected: false

    signal clicked()

    // ── Cover Art ──────────────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: "#1a1a1a"
        radius: 4
        border.color: selected ? "#00fff7" : "#222222"
        border.width: selected ? 2 : 1

        Image {
            id: coverImg
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: titleArea.top
            anchors.margins: 2
            source: root.movie && root.movie.cover_art_path ? "file:///" + root.movie.cover_art_path : ""
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
            asynchronous: true
            clip: true

            // Rounded corners mask
            layer.enabled: true
            layer.effect: ShaderEffectSource {
                sourceItem: Rectangle {
                    width: coverImg.width
                    height: coverImg.height
                    radius: 3
                    color: "black"
                }
            }
        }

        // Placeholder
        Rectangle {
            anchors.fill: parent
            color: "#1a1a1a"
            radius: 4
            visible: coverImg.status !== Image.Ready

            Text {
                anchors.centerIn: parent
                text: root.movie ? root.movie.title.charAt(0).toUpperCase() : ""
                color: "#333333"
                font.pixelSize: 32
                font.bold: true
            }
        }

        // ── Info Overlay ────────────────────────────────────────────────
        Rectangle {
            id: titleArea
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 56
            color: "#0a0a0a"
            opacity: 0.92
            radius: 4

            // Square off top corners
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 4
                color: parent.color
            }

            Column {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 2

                Text {
                    text: root.movie ? root.movie.title : ""
                    color: "#ffffff"
                    font.pixelSize: 11
                    font.bold: true
                    elide: Text.ElideRight
                    width: parent.width
                }

                Row {
                    spacing: 6
                    Text {
                        text: root.movie ? (root.movie.year || "") : ""
                        color: "#00fff7"
                        font.pixelSize: 9
                        font.family: "Consolas, monospace"
                    }
                    Text {
                        text: root.movie ? (root.movie.rating ? "★" + root.movie.rating.toFixed(1) : "") : ""
                        color: "#ffaa00"
                        font.pixelSize: 9
                        font.family: "Consolas, monospace"
                    }
                }

                Text {
                    text: root.movie ? (root.movie.genre || "") : ""
                    color: "#666666"
                    font.pixelSize: 9
                    elide: Text.ElideRight
                    width: parent.width
                }
            }
        }
    }

    // ── Hover Effect ───────────────────────────────────────────────────
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onEntered: root.scale = 1.03
        onExited: root.scale = 1.0
        onClicked: root.clicked()
    }

    Behavior on scale {
        NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
    }
}

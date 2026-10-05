import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import qs.Ui
import qs.Commons

Panel {
  id: root
  moduleName: "cam.resources"
  ipcTarget: moduleName
  property var metrics: ({rows: [], apps: [], level: 0})
  property string error: ""
  property bool ready: false
  readonly property color statusColor: !ready || error !== "" ? root.bar.foreground : metrics.level === 2 ? "#f7768e" : metrics.level === 1 ? "#e0af68" : "#9ece6a"
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  Process {
    id: sampler
    command: ["python3", Qt.resolvedUrl("metrics.py").toString().replace("file://", "")]
    running: true
    stdout: SplitParser {
      onRead: function(line) {
        try {
          var data = JSON.parse(line)
          if (data.error) root.error = data.error
          else { root.metrics = data; root.error = ""; root.ready = true }
        } catch (e) { root.error = "Unable to read resource data" }
      }
    }
    onExited: { root.error = "Monitor stopped; retrying…"; retry.start() }
  }
  Timer { id: retry; interval: 5000; onTriggered: sampler.running = true }

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "󰓅"
    foreground: root.statusColor
    tooltipText: "Computer resources · " + (root.ready ? (root.metrics.level === 2 ? "Near limits" : root.metrics.level === 1 ? "Getting busy" : "Room to spare") : "Loading")
    onPressed: function(b) { root.toggle() }
  }
  KeyboardPanel {
    id: popup
    anchorItem: button
    owner: root
    bar: root.bar
    open: root.opened
    focusTarget: keys
    contentWidth: popup.fittedContentWidth(Style.space(390))
    contentHeight: popup.fittedContentHeight(content.implicitHeight, Style.space(760))
    PanelKeyCatcher {
      id: keys
      anchors.fill: parent
      onCloseRequested: root.close()
      onTabRequested: function(direction) { root.switchPanel(direction) }
      ScrollView {
        id: scroll
        anchors.fill: parent
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: ScrollBar.AsNeeded
      Column {
        id: content
        width: scroll.availableWidth
        spacing: Style.space(14)
        Text {
          text: "Computer resources"
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.title
          font.bold: true
        }
        Text {
          width: parent.width
          wrapMode: Text.WordWrap
          text: root.error !== "" ? root.error : !root.ready ? "Sampling…" : root.metrics.level === 2 ? "Near limits · consider pausing heavy work" : root.metrics.level === 1 ? "Getting busy · keep an eye on headroom" : "Room to spare"
          color: root.statusColor
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.body
        }
        PanelSeparator { foreground: root.bar.foreground }
        Text {
          text: "Resource guard"
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.body
          font.bold: true
        }
        Text {
          width: parent.width
          text: root.metrics.guard_status || "Starting…"
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.caption
          wrapMode: Text.WordWrap
        }
        Text {
          text: root.metrics.guard_job || ""
          color: root.bar.foreground
          opacity: 0.7
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.caption
        }
        Repeater {
          model: root.metrics.rows
          Column {
            required property var modelData
            width: content.width
            spacing: Style.space(5)
            Text {
              text: modelData.label + "   " + modelData.value + "%"
              color: root.bar.foreground
              font.family: root.bar.fontFamily
              font.pixelSize: Style.font.body
              font.bold: true
            }
            Rectangle {
              width: parent.width
              height: Style.space(6)
              radius: height / 2
              color: Qt.rgba(1, 1, 1, 0.12)
              Rectangle {
                width: parent.width * Math.min(100, modelData.value) / 100
                height: parent.height
                radius: height / 2
                color: modelData.value >= 95 ? "#f7768e" : modelData.value >= 80 ? "#e0af68" : "#9ece6a"
              }
            }
            Text {
              width: parent.width
              text: modelData.detail
              color: root.bar.foreground
              opacity: 0.7
              font.family: root.bar.fontFamily
              font.pixelSize: Style.font.caption
              wrapMode: Text.WordWrap
            }
          }
        }
        PanelSeparator { foreground: root.bar.foreground }
        Text {
          text: "Largest apps by memory"
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.body
          font.bold: true
        }
        Repeater {
          model: root.metrics.apps
          Text {
            required property var modelData
            width: content.width
            textFormat: Text.PlainText
            text: modelData.name + "   " + modelData.memory
            elide: Text.ElideRight
            color: root.bar.foreground
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.caption
          }
        }
        Text {
          text: "Updates every 3 seconds · Esc to close"
          color: root.bar.foreground
          opacity: 0.5
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.caption
        }
      }
      }
    }
  }
}

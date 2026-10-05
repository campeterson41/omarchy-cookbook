import QtQuick
import qs.Ui
import qs.Commons

BarWidget {
  id: root
  moduleName: "cam.workspace"
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    iconComponent: Component {
      Item {
        Canvas {
          anchors.centerIn: parent
          width: 12
          height: 12
          property color ink: button.foreground
          onInkChanged: requestPaint()
          onPaint: {
            var c = getContext("2d")
            c.reset()
            c.scale(width / 19, height / 19)
            c.strokeStyle = ink
            c.lineWidth = 1.3
            c.lineCap = "round"
            c.lineJoin = "round"
            c.beginPath()
            c.moveTo(10, 5)
            c.lineTo(2, 5)
            c.lineTo(2, 15)
            c.lineTo(16, 15)
            c.lineTo(16, 11)
            c.moveTo(2, 5)
            c.lineTo(9, 10)
            c.lineTo(11, 8.5)
            c.moveTo(12, 6)
            c.lineTo(17, 1)
            c.moveTo(12.5, 1)
            c.lineTo(17, 1)
            c.lineTo(17, 5.5)
            c.stroke()
          }
        }
      }
    }
    slotSize: Style.bar.statusSlot
    tooltipText: "Open local dashboards"
    onPressed: function(b) {
      if (b === Qt.LeftButton && root.bar)
        root.bar.run("dashboard-workspace")
    }
  }
}

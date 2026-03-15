import { app } from "../../../scripts/app.js";

const showToast = (severity, summary, detail) => {
  app.extensionManager.toast.add({ severity, summary, detail, life: 3000 });
};

const nodeSettings = [
  {
    id: "Targm.Nodes.AllowAutoColoring",
    name: "Allow auto coloring",
    type: "boolean",
    defaultValue: true,
    tooltip: "Allow auto coloring for Targm nodes when created.",
    toastMsg: "Refresh your browser to apply changes.",
  },
];

app.registerExtension({
  name: "targm_settings_manager",
  settings: nodeSettings.map((s) => ({
    id: s.id,
    name: s.name,
    type: s.type,
    defaultValue: s.defaultValue,
    options: s.options,
    tooltip: s.tooltip,
    onChange: (value) => {
      const prevValue = app.ui.settings.getSettingValue(s.id);
      if (prevValue !== undefined && prevValue !== value) {
        showToast("warn", "Alert!", s.toastMsg);
      }
    },
  })),
});

app.registerExtension({
  name: "base.Targm",
  async nodeCreated(node) {
    const allow_auto_coloring = app.ui.settings.getSettingValue("Targm.Nodes.AllowAutoColoring");
    if (node.comfyClass !== "TARGM") {
      return;
    }
    if (allow_auto_coloring) {
      node.color = LGraphCanvas.node_colors.blue.color;
      node.bgcolor = LGraphCanvas.node_colors.cyan.bgcolor;
    }
  },
});

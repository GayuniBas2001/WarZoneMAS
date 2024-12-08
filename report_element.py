from mesa.visualization.ModularVisualization import VisualizationElement

class ReportElement(VisualizationElement):
    def __init__(self):
        self.package_includes = ["ChartModule.js"]
        self.jscode = """
        function ReportElement() {
            var container = document.createElement("div");
            container.id = "report-container";
            document.body.appendChild(container);

            this.render = function(data) {
                var report = data.report;
                if (report) {
                    var reportHtml = "<h3>Simulation Report</h3>";
                    for (var key in report) {
                        reportHtml += "<h4>" + key + "</h4><ul>";
                        for (var subKey in report[key]) {
                            reportHtml += "<li>" + subKey + ": " + report[key][subKey] + "</li>";
                        }
                        reportHtml += "</ul>";
                    }
                    container.innerHTML = reportHtml;
                }
            };

            this.reset = function() {
                container.innerHTML = "";
            };
        }
        """
    
    def render(self, model):
        return {"report": model.report}
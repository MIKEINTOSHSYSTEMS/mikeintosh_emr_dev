/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { getColor, hexToRGBA } from "@web/views/graph/colors";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const { Component, onWillStart, useEffect, useRef } = owl;

export class HIMSGraphField extends Component {
    setup() {
        this.chart = null;
        this.canvasRef = useRef("canvas");
        this.data = JSON.parse(this.props.value);

        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));

        useEffect(() => {
            this.renderChart();
            return () => {
                if (this.chart) {
                    this.chart.destroy();
                }
            };
        });
    }

    /**
     * Instantiates a Chart (Chart.js lib) to render the graph according to
     * the current config.
     */
    renderChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        let config;
        config = this.getLineChartConfig();
        this.chart = new Chart(this.canvasRef.el, config);
        // To perform its animations, ChartJS will perform each animation
        // step in the next animation frame. The initial rendering itself
        // is delayed for consistency. We can avoid this by manually
        // advancing the animation service.
        Chart.animationService.advance();
    }
    getLineChartConfig() {
        const labels = this.data[0].values.map(function (pt) {
            return pt.x;
        });
        const borderColor = this.data[0].is_sample_data ? hexToRGBA(getColor(10), 0.1) : getColor(10);
        const backgroundColor = this.data[0].is_sample_data ? hexToRGBA(getColor(10), 0.05) : hexToRGBA(getColor(10), 0.2);
        let line_data;
        line_data = [
            {
                backgroundColor,
                borderColor: this.data[0].color,
                data: this.data[0].values,
                fill: "start",
                label: this.data[0].key,
                borderWidth: 2,
            },
        ]

        if (this.data.length>=2) {
            line_data = [
                {
                    backgroundColor,
                    borderColor: this.data[0].color,
                    data: this.data[0].values,
                    fill: "start",
                    label: this.data[0].key,
                    borderWidth: 2,
                },
                {
                    backgroundColor,
                    borderColor: this.data[1].color,
                    data: this.data[1].values,
                    fill: "start",
                    label: this.data[1].key,
                    borderWidth: 2,
                },
            ]

        }

        return {
            type: "line",
            data: {
                labels,
                datasets: line_data,
            },
            options: {
                legend: { display: false },
                scales: {
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: this.props.ylabel,
                            fontSize: 14
                        }
                    }],
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: this.props.xlabel,
                            fontSize: 14
                        }
                    }]
                },
                maintainAspectRatio: false,
                elements: {
                    line: {
                        tension: 0.000001,
                    },
                },
                tooltips: {
                    intersect: false,
                    position: "nearest",
                    caretSize: 0,
                },
            },
        };
    }
}

HIMSGraphField.template = "yan_hims_tasks.HIMSGraphField";
HIMSGraphField.props = {
    ...standardFieldProps,
    xlabel: String,
    ylabel: String,
};

HIMSGraphField.supportedTypes = ["text"];

HIMSGraphField.extractProps = ({ attrs }) => {
    return {
        xlabel: attrs.xlabel,
        ylabel: attrs.ylabel,
    };
};

registry.category("fields").add("HIMSGraph", HIMSGraphField);

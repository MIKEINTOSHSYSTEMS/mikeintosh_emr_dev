/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formatFloatTime } from "@web/views/fields/formatters";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const { Component, useState, onWillUpdateProps, onWillStart, onWillDestroy } = owl;

export class YanTimer extends Component {
    setup() {
        super.setup();
        this.state = useState({
            duration:
                this.props.duration !== undefined
                    ? this.props.duration
                    : this.props.record.data[this.props.duration_field],
        });

        const newLocal = this;
        let timer_running;
        timer_running = 0;
        if (this.props.record.data[this.props.yan_timer_start_field]){
            timer_running = 1;
        }
        if (this.props.record.data[this.props.yan_timer_start_field] && this.props.record.data[this.props.yan_timer_end_field]){
            timer_running = 0;
        }
        console.log("this----",this,timer_running);
        
        this.ongoing =
            this.props.ongoing !== undefined
                ? newLocal.props.ongoing
                : timer_running;

        onWillStart(() => this._runTimer());
        onWillUpdateProps((nextProps) => {
            this.ongoing = nextProps.ongoing;
            this._runTimer();
        });
        onWillDestroy(() => clearTimeout(this.timer));
    }

    get duration() {
        // formatFloatTime except 1,5 =  1h30min but in this case 1,5 = 1min30
        return formatFloatTime(this.state.duration / 60, { displaySeconds: true });
    }

    _runTimer() {
        if (this.ongoing) {
            this.timer = setTimeout(() => {
                this.state.duration += 1 / 60;
                this._runTimer();
            }, 1000);
        }
    }
}

YanTimer.supportedTypes = ["float"];
YanTimer.template = "yan_web_timer.YanTimeCounter";

YanTimer.props = {
    ...standardFieldProps,
    yan_timer_start_field: String,
    yan_timer_stop_field: String,
    duration_field: String,
};

YanTimer.extractProps = ({ attrs }) => {
    return {
        yan_timer_start_field: attrs.options.widget_start_field,
        yan_timer_stop_field: attrs.options.widget_stop_field,
        duration_field: attrs.options.duration_field,
    };
};

registry.category("fields").add("YanTimer", YanTimer);

import React from 'react';
import createPlotlyComponent from 'react-plotly.js/factory';
import Plotly from 'plotly.js-dist-min';

const Plot = createPlotlyComponent(Plotly);

export default function SafePlot(props) {
  try {
    return <Plot {...props} />;
  } catch (err) {
    return <div className="text-red-400 p-4 text-center">خطا در بارگذاری نمودار</div>;
  }
}

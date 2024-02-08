$(document).ready(function () {  
    var PatientPortalData = $("input[name='patient_portal_line_graph']").val();

    if (PatientPortalData){
        YANPatientChartData = JSON.parse(PatientPortalData);
        new Chart(document.getElementById("YANPatientLineChart"), {
            type: 'line',
            data: YANPatientChartData,
            options: {
              scales: {
                xAxes: [{
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45,
                    }
                }]
              }
            }
        });

    }
});
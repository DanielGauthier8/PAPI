// Displays a HTML table, giving instructors insight as to 

const cellColor = (ratio, hex) => {
    // Uses ratio to return an apporatiate color '
    return hex.map(color => {
        return color === 0 ? parseInt(ratio * 55) + 200 : color; 
    })
}

const displayHeatMap = (data, inserts, deletes) => {

    inserts = parseInt(inserts);
    deletes = parseInt(deletes)
    
    $("#heatmap").append(data.map(point => {
        return "<tr><td>" + point.time.format() + " </td><td style='background-color: rgb(" + cellColor(point.i/inserts, [1, 0, 1]) + ")'>" + 
            point.i + "</td><td style='background-color: rgb(" + cellColor(point.d/deletes, [0, 1, 1]) + ")'>" + point.d + "</td></tr>"  
    }))

}
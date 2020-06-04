// Displays a HTML table, giving instructors insight as to 

const cellColor = (ratio, hex) => {
    // Uses ratio to return an apporatiate color
    return hex.map(color => {
        return color === 0 ? parseInt(ratio * 55) + 200 : color; 
    })
}

// @todo: Add heatmap time frame? (e.g., 8 hours, 4 hours, hourly, etc)

const displayHeatMap = (input, inserts, deletes) => {

    // Import data from JSON
    data = [];
    Object.keys(input).forEach(key => {
        data.push({time: moment(input[key].time), i: input[key].o === "i" ? 1 : 0, d: input[key].o === "d" ? 1 : 0})
    })


    // Re-organize data by date 
    var dates = {};
    var current_time_block = 1;
    var current_date = data[0].time;

    for(var i = 0; i < data.length; i++){
        // Create obj key for date
        if( dates[data[i].time.format("MDYY")] === undefined){
            dates[data[i].time.format("MDYY")] = [];
            dates[data[i].time.format("MDYY")][99] = data[i].time;
        }

        // Create array item for hour (split into 3 blocks per day?)
        if(dates[data[i].time.format("MDYY")][Math.floor(parseInt(data[i].time.format('H')) / 8)] === undefined){
            dates[data[i].time.format("MDYY")][Math.floor(parseInt(data[i].time.format('H')) / 8)] = {i: 0, d: 0};  
        }

        // Push inserts and deletions from that timeframe into the obj
        dates[data[i].time.format("MDYY")][Math.floor(parseInt(data[i].time.format('H')) / 8)].i += data[i].i;
        dates[data[i].time.format("MDYY")][Math.floor(parseInt(data[i].time.format('H')) / 8)].d += data[i].d;
    }

    console.log(dates)

    inserts = parseInt(inserts);
    deletes = parseInt(deletes)

    var table = "";
    Object.keys(dates).forEach(key => {
        console.log(dates[key])
        table += "<tr><td>" + dates[key][99].format("MM/DD/YYYY") + "</td>"
        for(var i = 0; i < 3; i++){
            table += dates[key][i] === undefined ? 
                "<td></td>" : "<td style=\"color: white; background: linear-gradient(90deg, rgb(" + cellColor(dates[key][i].i, [1, 0, 1])+ ") 0%, rgb(" + cellColor(dates[key][i].i, [0, 1, 1])+ ") " + Math.floor(((dates[key][i].i - dates[key][i].d) / ((dates[key][i].i + dates[key][i].d) / 2)) * 100) + "%)\">inserts: " + dates[key][i].i + " / deletes:" + dates[key][i].d + "</td>";
        }

    })

    $("#heatmap").append(table);

}
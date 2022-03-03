// mon
'use strict';
let MonRefresh = MONSERVERREFRESH;  // 1000 ms = every second
let powerGauge;
let myMinValue = 0.5;
let myMaxValue = 50000;

var VarNames      = ["datetime",
                     "cpm", "cps", "cpm1st", "cps1st", "cpm2nd", "cps2nd", "cpm3rd", "cps3rd",
                     "temp", "press", "humid", "airq",
                     "sensitivityDef", "sensitivity1st", "sensitivity2nd", "sensitivity3rd",
                     "limitLo", "limitHi",
                    ];
var LastAvgData   = [];
var TubeIndex     = 0;
var oldTubeIndex  = 0;
var LogStatus     = 0; // not logging


async function getLastData(){
    splittext = await fetchRecord('/lastdata');
    console.log("splittext:", splittext);

    LastAvgData[VarNames[0]]  = splittext[0];       // must be separate as non-numeric variable! can't use '+'
    for (let i = 1; i <= 18; i++){
        LastAvgData[VarNames[i]] = +splittext[i];
    }
    // console.log(LastAvgData);

    if (LastAvgData[VarNames[0]] == "Available when logging"){LogStatus = 0;}
    else                                                     {LogStatus = 1;}

    TubeIndex    = document.getElementById("vars").selectedIndex;
    oldTubeIndex = TubeIndex;
    // console.log("TubeIndex: ", TubeIndex)

    let usvvalue;
    if      (TubeIndex == 0)    usvvalue = LastAvgData["cpm"]    / LastAvgData["sensitivityDef"];
    else if (TubeIndex == 1)    usvvalue = LastAvgData["cpm1st"] / LastAvgData["sensitivity1st"];
    else if (TubeIndex == 2)    usvvalue = LastAvgData["cpm2nd"] / LastAvgData["sensitivity2nd"];
    else if (TubeIndex == 3)    usvvalue = LastAvgData["cpm3rd"] / LastAvgData["sensitivity3rd"];
    // console.log("usvvalue: ", usvvalue)

    document.getElementById("cpm").innerHTML = getNumFormat(LastAvgData[VarNames[1 + TubeIndex * 2]]);
    document.getElementById("cps").innerHTML = getNumFormat(LastAvgData[VarNames[1 + TubeIndex * 2]] / 60);
    document.getElementById("usv").innerHTML = getNumFormat(usvvalue);

    document.getElementById("temp"  ).innerHTML = getNumFormat(LastAvgData["temp"]);
    document.getElementById("press" ).innerHTML = getNumFormat(LastAvgData["press"]);
    document.getElementById("humid" ).innerHTML = getNumFormat(LastAvgData["humid"]);
    document.getElementById("airq"  ).innerHTML = getNumFormat(LastAvgData["airq"]);
}

function makePowerGauge(){
    // this only creates the instance; it does not render the graph

    TubeIndex       = document.getElementById("vars").selectedIndex;
    oldTubeIndex    = TubeIndex;
    let sensitvalue = LastAvgData[VarNames[13 + TubeIndex]];
    let lt, ht;
    if (!isNaN(sensitvalue)){
        lt = LastAvgData["limitLo"] * sensitvalue;
        ht = LastAvgData["limitHi"] * sensitvalue;
    }
    else{
        lt = 0.5;
        ht = 0.5;
    }
    console.log("sensitvalue", sensitvalue, "lowthresh:", lt, "highthresh: ", ht);

    let col1, col2, col3;
    if (LogStatus == 1){
        col1 = '#00C853';
        col2 = '#ffe500';
        col3 = '#EA4335';
    }
    else{
        col1 = '#ccc';
        col2 = '#aaa';
        col3 = '#888';
    }
    powerGauge = new Gauge({
        size                : 340,
        minValue            : myMinValue,
        maxValue            : myMaxValue,
        lowThreshhold       : lt,
        highThreshhold      : ht,
        majorTicks          : 5,  // is ignored when in logScale
        scale               : 'log',
        displayUnit         : 'CPM',
        transitionMs        : 200,
        lowThreshholdColor  : col1,
        defaultColor        : col2,
        highThreshholdColor : col3,
    });
}

async function MonMain(){

    BusyCursor();

    document.title = "";

    await getLastData();

    makePowerGauge();
    console.log("powerGauge MonMain(): min, max:", powerGauge.config.minValue, powerGauge.config.maxValue, "transitionMs:", powerGauge.config.transitionMs);
    powerGauge.render("#gauge");

    TubeIndex = document.getElementById("vars").selectedIndex;
    let cpmcounts = LastAvgData[VarNames[1 + TubeIndex * 2]];      // use cpm, cpm1st, ...
    console.log("cpmcounts", cpmcounts)
    powerGauge.update(cpmcounts);

    setInterval(function() {
        getLastData();
        TubeIndex = document.getElementById("vars").selectedIndex;
        if (TubeIndex != oldTubeIndex){
            console.log("Tubeindex changed: old:", oldTubeIndex, ", new:", TubeIndex);
            if (newgauge == 0){
                makePowerGauge();
                document.getElementById("gauge").innerHTML = "";
                d3.selectAll("svg").remove();
                powerGauge.rerender("#gauge");
            }
            else{ //{newgauge == 2)
                let sensitvalue = LastAvgData[VarNames[13 + TubeIndex]];
                let lt, ht;
                if (!isNaN(sensitvalue)){
                // if (isNaN(sensitvalue)){
                    lt = LastAvgData["limitLo"] * sensitvalue;
                    ht = LastAvgData["limitHi"] * sensitvalue;
                }
                else{
                    lt = 0.5;
                    ht = 0.5;
                }
                console.log("sensitvalue", sensitvalue, "lowthresh:", lt, "highthresh: ", ht);
                let newconfig = {lowThreshhold: lt, highThreshhold:ht}
                powerGauge.setConfig(newconfig).render("#gauge");
            }
        }

        cpmcounts    = LastAvgData[VarNames[1 + TubeIndex * 2]];

        powerGauge.update(cpmcounts);

    }, MonRefresh);

    NormalCursor();
}

MonMain();


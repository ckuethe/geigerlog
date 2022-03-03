// avg
'use strict';
// var AvgRefresh    = 10000       // = 10 sec
var AvgRefresh    = MONSERVERREFRESH // 10000 ms = 10 sec
var chunk         = 0;          // DeltaT in min
var VarNames      = ["datetime",                                                                    // 1    1   0
                     "cpm", "cps", "cpm1st", "cps1st", "cpm2nd", "cps2nd", "cpm3rd", "cps3rd",      // 8    9   8
                     "temp", "press", "humid", "airq",                                              // 4    13  12
                     "DeltaT",                                                                      // 1    14  13
                     "sensitivityDef", "sensitivity1st", "sensitivity2nd", "sensitivity3rd",        // 4    18  17
                     "usvDef", "usv1st", "usv2nd", "usv3rd"                                         // 4    22  21
                    ];
var LastAvgData   = [];

// get Avg data for DeltaT
async function AvgGetDataRecord(DeltaT){

    let dataSource      = "/lastavg?chunk=" + DeltaT;

    // Get the data
    splittext = await fetchRecord(dataSource);
    console.log("splittext:", splittext);

    LastAvgData[VarNames[0]] = splittext[0];    // no '+'!
    for (let i = 1; i <= 17; i++){
        LastAvgData[VarNames[i]] = +splittext[i];
    }
    LastAvgData["usvDef"] = LastAvgData["cpm"]    / LastAvgData["sensitivityDef"];
    LastAvgData["usv1st"] = LastAvgData["cpm1st"] / LastAvgData["sensitivity1st"];
    LastAvgData["usv2nd"] = LastAvgData["cpm2nd"] / LastAvgData["sensitivity2nd"];
    LastAvgData["usv3rd"] = LastAvgData["cpm3rd"] / LastAvgData["sensitivity3rd"];
    // console.log("LastAvgData: ", LastAvgData)

    return LastAvgData;
};


async function AvgInsertRecords(type, DeltaT){
    // type is: "", "A", or "B" for 1st, 2nd, 3rd column

    console.log("AvgInsertRecords: type: '" + type + "', DeltaT: " + DeltaT);

    let data = await AvgGetDataRecord(DeltaT);

    for (let i of [1,2,3,4,5,6,7,8,9,10,11,12,   18,19,20,21]){
        document.getElementById(VarNames[i] + type).innerHTML = getNumFormat(data[VarNames[i]]);
    }
    document.getElementById("recs" + type).innerHTML = data["DeltaT"] + "min";
}


async function AvgAddOn(){

    await AvgInsertRecords("",   1);
    await AvgInsertRecords("A",  3);
    await AvgInsertRecords("B", 10);
}


function AvgStartFetchTimer(){

    if(TimerIsRunning()) return;

    FetchTimerID = setInterval(function() {AvgAddOn();}, AvgRefresh) ;
    console.log("FetchTimer started");
}


function AvgStopFetchTimer(){

    if (! TimerIsRunning()) return;

    clearInterval(FetchTimerID);
    FetchTimerID = null;
    console.log("FetchTimer stopped");
}

async function AvgMain(){

    BusyCursor();

    document.title = "";
    await AvgAddOn();
    AvgStartFetchTimer();

    NormalCursor();
}

AvgMain();


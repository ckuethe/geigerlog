// console.log("am_common_js was loaded");

var splittext;
var FetchTimerID    = null;     // ID of interval timer

function BusyCursor()       {document.body.style.cursor = 'wait';}
function NormalCursor()     {document.body.style.cursor = 'default';}
function isNumber(value)    {return typeof value === 'number' && isFinite(value);}


// used for 1-line record types: lastdata, lastavg
async function fetchRecord(RecordType){
    let fetchDataText = "";
    try{
        const fetchData = await fetch(RecordType, {cache: "no-store"});
        fetchDataText   = await fetchData.text();
        // console.log("fetchDataText", fetchDataText)
        if (fetchDataText.startsWith("<!")) fetchDataText = "HTML";
    }
    catch(error){
        console.log("ERROR: fetchRecord:", error);
    }
    return fetchDataText.split(",");
}


function getNumFormat(number){
    if      (isNaN(number))   return "---";
    else if (number >= 10000) return number.toFixed(0);
    else if (number >= 900)   return number.toFixed(1); // to allow P from 900.0 to >1030.9
    else if (number >= 100)   return number.toFixed(1);
    else                      return number.toFixed(2);
}


function TimerIsRunning(){
    if((FetchTimerID === null)) return false;
    else                        return true;
}


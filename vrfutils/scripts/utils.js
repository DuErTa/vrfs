/**
 * Created by tamir on 10/07/17.
 */

function toggle_class(elemID, class1, class2) {
    var currElem = document.getElementById(elemID);
    if (currElem.className == class1) {
        currElem.className = class2;
    }
    else {
        currElem.className = class1;
    }
}


function toggle_innerhtml(elemID, html1, html2) {
    var currElem = document.getElementById(elemID);
    if (currElem.innerHTML == html1) {
        currElem.innerHTML = html2;
    }
    else {
        currElem.innerHTML = html1;
    }
}

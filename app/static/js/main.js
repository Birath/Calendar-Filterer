var elem = document.querySelector('.collapsible');
var instance = M.Collapsible.init(elem, {});

function addNewCal(elem) {
    elem.innerHTML = "" +
        "<div class='input-field'>" +
        "  <input type='text' name='new-cal-name' id='new-cal-name'>" +
        "  <label for='new-cal-name'>Name of the new calendar</label>" +
        "</div>"
}

function getFilterID(elem) {
    var id = $(elem).attr('id');
    if (id === 'last-filter') {
        return filterNum;
    }
    else {
        return id.substr(-1);
    }
}

function sortFn(a, b) {
    if (a > b) return 1;
    if (a < b) return -1;
    return 0;
}


$.fn.ignore = function(sel){
  return this.clone().find(sel||">*").remove().end();
};


function updateFilters() {
    var filterID = 0;
    $('#filter-list').children().each(function () {
        var filter = $(this);
        if (filter.prop("tagName") === 'DIV') return true;
        if (filter.attr('id') !== 'filter-adder') {
            if (filter.children().first().ignore("i").text().indexOf("Filter #") >= 0) {
                var visualFilterID = filterID + 1;
                filter.children().first().html("<i class=\"material-icons\">filter_list</i> Filter #"+ visualFilterID);
            }
            if (filterID === filterNum) {
                filter.attr('id', 'last-filter');
            }
            else {
                filter.attr('id', 'filter' + filterID);
            }
            filterID++;
        }
    })
}


function getFilterBody(filterID) {
    var filterVisual = filterID + 1;
    return "" +
    "<li class id=\"last-filter\">\n" +
    "    <div class=\"collapsible-header\"><i class=\"material-icons\">filter_list</i>Filter #"+ filterVisual + "</div>\n" +
    "    <div class=\"collapsible-body filter-body\">\n" +
    "        <div class=\"row\"> \n" +
    "           <div class=\"col s6 input-field\">\n" +
    "               <input type=\"text\" name=\"course-code"+filterID+"\" id=\"autocomplete-input"+ filterID +"\" autocomplete=\"off\" class=\"autocomplete\">\n" +
    "                   <label for=\"autocomplete-input" +filterID+"\">Course Code</label>\n" +
    "           </div>\n" +
    "           <div class=\"col s6 input-field\">\n" +
    "               <input type=\"text\" name=\"description"+filterID+"\" id=\"description"+ filterID +"\">\n" +
    "               <label for=\"description" +filterID+ "\">Description</label>\n" +
    "           </div>\n" +
    "           <div class=\"col s6 input-field\">\n" +
    "               <input type=\"text\" name=\"group-name"+filterID+"\" id=\"group-name"+ filterID +"\">\n" +
    "               <label for=\"group-name"+ filterID +"\">Group Name</label>\n" +
    "           </div>\n" +
    "           <div class=\"col s6\">\n" +
    "               <button type=button class=\"btn-flat waves-light waves-effect red white-text delete-btn right\">delete</button>\n" +
    "           </div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</li>";
}


function getFilterVals() {
    var filterData =  [];
    var filterIndex = 0;
    $('#filter-list').children("li").each(function () {
        var filter = $(this);
        var currentFilterData = [];
        filter.children(".collapsible-body").find("input").each(function () {
            currentFilterData.push(($(this).val()));
        });
        filterData.push(currentFilterData.concat());
        filterIndex++;
    });
    console.log(filterData);
    return filterData
}


var filterNum = 0;
$('#add-filter').on('click', function () {
    if ($('#filter-list').children().length === 2 ) {
        console.log("No filters");
        $('#add-filter').parent().before(function () {
            return getFilterBody(filterNum);
        }
    )}
    else {
        $('#last-filter').after(function () {
            $('#last-filter').attr('id', 'filter' + filterNum);
            filterNum++;
            return getFilterBody(filterNum);
        }
    )}
    instance.open(filterNum);
});

$('body').on('click', '.delete-btn', function () {
    console.log($(this).parents().eq(2));
    $(this).parents().eq(3).remove();
    if (filterNum > 0) {
        filterNum--;
    }
    updateFilters()
});

var newCal = true;
$('body').on('click', '#cal-chooser', function () {
    var calChoice  =  $(this);
    var input = calChoice.children().children("input");
    // Ignores if already checked
    if (input.prop("checked") === true) {
        return;
    }
    input.prop("checked", true);
    if (calChoice.attr('class') === "collection-item new-cal") {
        // Adds input for the name of the new cal
        if (newCal) {
            var oldHeight = calChoice.css('height');
            calChoice.html("" +
                "<div class='new-cal-name row valign-wrapper'>" +
                "  <div class='col s4'>" +
                "    <label>\n" +
                "      <input class=\"with-gap\" name=\"calendar\" type=\"radio\" id=\"calendar\"/>\n" +
                "      <span id='new-cal'>New calendar</span>\n" +
                "    </label>" +
                "  </div>" +
                "  <div class='col s8 new-cal-name-input input-field'>" +
                "    <input type='text' name='new-cal-name' id='new-cal-name'>" +
                "    <label for='new-cal-name'>Calendar name</label>" +
                "  </div>" +
                "</div>" );
            newCal = false;
            var newHeight = $(this).css('height');
            calChoice.css({'height': oldHeight});
            calChoice.animate({'height': newHeight}, 300)
        }
        // Checks the new checkbox
        calChoice.find("input").first().prop("checked", true);
    }
});

$('body').on('focus',"input.autocomplete" ,function () {
    $.getJSON("static/data/course_data.json", function( json ) {
        $('input.autocomplete').autocomplete({
            data: json,
            limit: 4,
            minLength: 2,
            sortFunction: sortFn
        });
    });
});

$('body').on('focusout','[id^=autocomplete-input]', function () {
    /*
    Changes the title of the filter to the selected course
    */
    if ($(this).val().length < 5) {
        return;
    }
    console.log($(this).parents().eq(3).children().first().html("<i class=\"material-icons\">filter_list</i>" + "Filter for: " + $(this).val() ));
});


function getProgress(status_url) {
    // Uses an eventsource to stream the progress of adding the calendar events
    $.getJSON(status_url, function (data) {
        if (data['state'] === 'SUCCESS') {
            var percent = parseInt(data['current'] * 100 / data['total']);
            console.log(percent);
            $('#progress').attr('style', "width: " + percent + '%');
        }
        else if (data['state'] !== 'FAILURE')  {
            var percent = parseInt(data['current'] * 100 / data['total']);
            console.log(percent);
            $('#progress').attr('style', "width: " + percent + '%');
            setTimeout(function () {
                getProgress(status_url)
            }, 100)
        }
    });
}

$(document).ready(function(){
    $.getJSON("static/data/course_data.json", function( json ) {
        $('input.autocomplete').autocomplete({
            data: json,
            limit: 4,
            minLength: 2,
            sortFunction: sortFn
        });
    });
    $('body').on('submit', '#calender-data', function (event) {
        event.preventDefault();
        console.log('Submitting');
        var filterData = getFilterVals();
        console.log(filterData);
        var sendData = {};
        var outCalendar = $('input[name="calendar"]:checked');
        var outCalendarName = outCalendar.siblings("span").text();
        var newCal = false;
        if (outCalendar.siblings("span").attr('id') === "new-cal") {
            outCalendarName = $('#new-cal-name').val();
            newCal = true;
        }
        sendData["filters"] = filterData;
        sendData['out-calendar'] = outCalendarName;
        sendData['calendar-url'] = $('#calendar-url').val();
        sendData['new-cal'] = newCal;
        $.ajax({
            type: "GET",
            url: 'filterer_test',
            dataType: 'text',
            data: sendData,
            success: function (data, status, request) {
                var status_url = request.getResponseHeader('Location');

                console.log('completed');
                getProgress(status_url)
            }
        });
    });

});
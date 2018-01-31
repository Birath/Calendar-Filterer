var elem = document.querySelector('.collapsible');
var instance = M.Collapsible.init(elem, {});



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
        console.log(filter.prop('tagName'));
        if (filter.prop("tagName") === 'DIV') return true;
        if (filter.attr('id') !== 'filter-adder') {
            if (filter.children().first().ignore("i").text().indexOf("Filter #" >= 0)) {
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
    var filterData =  {};
    console.log(filterData);
    $('#filter-list').children("li").each(function () {
        var filter = $(this);
        console.log(filter.children(".collapsible-body").find("input").each(function () {
            filterData[$(this).attr('id')] = ($(this).val())
        }));
    });
    return filterData
}


var filterNum = 0;
$('#add-filter').on('click', function () {
    if ($('#filter-list').children().length === 1 ) {
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

$('body').on('click', '#cal-chooser', function () {
    console.log($(this).children().children("input").prop("checked", true))
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


$(document).ready(function(){
    $.getJSON("static/data/course_data.json", function( json ) {
        $('input.autocomplete').autocomplete({
            data: json,
            limit: 4,
            minLength: 2,
            sortFunction: sortFn
        });
    });
    $('body').on('submit', '#calender-data', function () {
        event.preventDefault();
        console.log('Submitting');
        var filterData = getFilterVals();
        console.log(filterData);
        filterData['out-calendar'] = $('input[name="calendar"]:checked').siblings("span").text();
        filterData['calendar-url'] = $('#calendar-url').val();
        $.ajax({
            type: "GET",
            url: 'filterer_test',
            dataType: 'json',
            data: filterData,
            success: function (data) {
                console.log('we did it')
            }
        });
    });

});


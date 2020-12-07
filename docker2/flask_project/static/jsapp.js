/*
SOURCE:
https://www.youtube.com/watch?v=Kcka5WBMktw
*/


$(document).ready(function() {

    $(document).on('click', '.editButton', function() {

        var contact_id = $(this).attr('unique_id');

        var phone = $('#phoneInput'+contact_id).val();
        var email = $('#emailInput'+contact_id).val();
        var role = $('#roleInput'+contact_id).val();

        req = $.ajax({
            url : '/editcontact',
            type : 'POST',
            data : { phone : phone, email : email, id : contact_id, role : role }
        });

        req.done(function(data) {

            $('#contactSection'+contact_id).fadeOut(1000).fadeIn(1000);
            $('#contactSection'+contact_id).html(data);

        });

    });


    $(document).on('click', '.deleteButton', function() {

        var contact_id = $(this).attr('unique_id');

        req = $.ajax({
            url : '/deletecontact',
            type : 'POST',
            data : {  id : contact_id }
        });

        req.done(function(data) {

            $('#contactSection'+contact_id).html(data);

        });

    });


    $(document).on('click', '.querySearchButton', function() {

        var querySearch_id = $(this).attr('unique_id');

        var querySearch = $('#querySearchInput'+querySearch_id).val();

        req = $.ajax({
            url : '/newquerysearch',
            type : 'POST',
            data : {  search : querySearch, id : querySearch_id }
        });

        req.done(function(data) {

            $('#querySearchSection'+querySearch_id).html(data);

        });

    });


    $(document).on('click', '.querySaveButton', function() {

        var qS_id = $(this).attr('unique_id');
        var cheAndEntry = $('#querySaveInput'+qS_id).val();

        req = $.ajax({
            url : '/savequery',
            type : 'POST',
            data : {  id : qS_id, cheAndEntry : cheAndEntry }
        });

        req.done(function(data) {

            $('#querySearchSection'+qS_id).html(data);

    });

});


    $(document).on('click', '.queryDeleteButton', function() {

        var saved_id = $(this).attr('unique_id');

        req = $.ajax({
            url : '/deletequery',
            type : 'POST',
            data : {  id : saved_id }
        });

        req.done(function(data) {

            $('#querySavedSection'+saved_id).html(data);

        });

    });


    $(document).on('click', '.redirectQueryButton1', function() {

        var querySearch_id = $(this).attr('unique_id');

        var querySearch = $('#newQuerySearch1'+querySearch_id).val();

        req = $.ajax({
            url : '/newquerysearch',
            type : 'POST',
            data : {  search : querySearch, id : querySearch_id }
        });

        req.done(function(data) {

            $('#querySearchSection'+querySearch_id).html(data);

        });

    });


    $(document).on('click', '.redirectQueryButton2', function() {

        var querySearch_id = $(this).attr('unique_id');

        var querySearch = $('#newQuerySearch2'+querySearch_id).val();

        req = $.ajax({
            url : '/newquerysearch',
            type : 'POST',
            data : {  search : querySearch, id : querySearch_id }
        });

        req.done(function(data) {

            $('#querySearchSection'+querySearch_id).html(data);

        });

    });


    $(document).on('click', '.redirectQueryButton3', function() {

        var querySearch_id = $(this).attr('unique_id');

        var querySearch = $('#newQuerySearch3'+querySearch_id).val();

        req = $.ajax({
            url : '/newquerysearch',
            type : 'POST',
            data : {  search : querySearch, id : querySearch_id }
        });

        req.done(function(data) {

            $('#querySearchSection'+querySearch_id).html(data);

        });

    });


});

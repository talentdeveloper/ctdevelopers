$(document).ready(function() {
    $('.note-history').on('click', '.btn-delete-note', function() {
        var user_note_pk = $(this).attr('data-user-note-pk');

        $.ajax({
            context: this,
            type: 'POST',
            url: Urls['users:user_note_delete'](user_note_pk),
            dataType: "json",
            success: function(response) {
                if (response.success) {
                    var note_history_item = $(this).closest('.note-history-item').remove();

                    var note_history = $('.note-history');
                    if (note_history.find('.note-history-item').length == 0) {
                        note_history.html('<div class="no-history">No history yet.</div>')
                    }
                }
                else {
                    $.each(response.errors, function(key, value){
                        alert(value);
                    })
                }
            }
        });
    });

    $('.note-history').on('click', '.btn-edit-note', function() {
        $(this).closest('.note-history-item-details').addClass('hidden');
        $(this).closest('.note-history-item').find('.edit-note-form').removeClass('hidden');
    });

    $('.note-history').on('click', '.btn-save-edit-note', function(event) {
        event.preventDefault();
        var form = $(this).closest('.edit-note-form');

        $.ajax({
            context: this,
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            dataType: "json",
            success: function(response) {
                if (response.success) {
                    var type = '';
                    if (response.data.type == 1)
                        type = '<i class="glyphicon glyphicon-phone"></i>';
                    else if (response.data.type == 2)
                        type = '<i class="glyphicon glyphicon-earphone"></i>';
                    else if (response.data.type == 3)
                        type = '<i class="glyphicon glyphicon-envelope"></i>';

                    var note_history_item = $(this).closest('.note-history-item');
                    note_history_item.find('.user-note-type-icon').html(type);
                    note_history_item.find('.user-note-text').html(response.data.text);

                    note_history_item.find('.edit-note-form').addClass('hidden');
                    note_history_item.find('.note-history-item-details').removeClass('hidden');
                }
                else {
                    $.each(response.errors, function(key, value){
                        var form_error = key + '_error';
                        form.find('.' + form_error).html(value);
                    })
                }
            }
        });
    });

    $('.btn-cancel-create-note').on('click', function(event) {
        event.preventDefault();
        $('.create-note-form').addClass('hidden');
    });

    $('.btn-show-create-note').on('click', function(event) {
        event.preventDefault();
        $('.create-note-form').removeClass('hidden');
    });

    $('.btn-create-note').on('click', function(event) {
        event.preventDefault();
        $('.error').html('');
        $('.create-note-form').ajaxSubmit({
            success: function (response) {
                if (response.success) {
                    $('.no-history').html('');
                    $.each($('.create-note-form').find('.note-type'), function(key, value){
                        $(this).removeClass('active');
                    });
                    $('.create-note-form').find('#id_text').val('');
                    $('.create-note-form').find('#id_type').val('');

                    var type = '';
                    if (response.data.type == 1)
                        type = '<i class="glyphicon glyphicon-phone"></i>';
                    else if (response.data.type == 2)
                        type = '<i class="glyphicon glyphicon-earphone"></i>';
                    else if (response.data.type == 3)
                        type = '<i class="glyphicon glyphicon-envelope"></i>';

                    var text_type = '<i class="glyphicon glyphicon-phone note-type';
                    var call_type = '<i class="glyphicon glyphicon-earphone note-type';
                    var mail_type = '<i class="glyphicon glyphicon-envelope note-type';

                    if (response.data.type == 1)
                        text_type += ' active';
                    else if (response.data.type == 2)
                        call_type += ' active';
                    else if (response.data.type == 3)
                        mail_type += ' active';

                    text_type += '" data-type="1"></i> &nbsp;';
                    call_type += '" data-type="2"></i> &nbsp;';
                    mail_type += '" data-type="3"></i>';

                    var html =
                        '<div class="row note-history-item">\
                            <div class="note-history-item-details">\
                                <div class="row">\
                                    <div class="col-md-9">\
                                        <span class="note-history-timestamp">' + response.data.created_at.proper + ' <strong>' + response.data.created_at.timeago + '</strong></span>\
                                    </div>\
                                    <div class="col-md-3 text-right">\
                                        <span class="note-history-timestamp">\
                                            <i class="glyphicon glyphicon-pencil btn-action-note-history btn-edit-note"></i>\
                                            <i class="glyphicon glyphicon-remove btn-action-note-history btn-delete-note orange-text" data-user-note-pk=' + response.data.pk + '></i>\
                                        </span>\
                                    </div>\
                                </div>\
                                <div class="row note-item-text">\
                                    <div class="col-md-1 user-note-type-icon">\
                                        ' + type + '\
                                    </div>\
                                    <div class="col-md-11 user-note-text">\
                                        ' + response.data.text + '\
                                    </div>\
                                </div>\
                            </div>\
                            <form action="' + Urls['users:user_note_update'](response.data.pk) + '" method="POST" class="edit-note-form hidden">\
                                <input type="hidden" name="csrfmiddlewaretoken" value="' + response.data.csrf_token + '">\
                                <input type="hidden" name="note_to" id="id_note_to" value="' + response.data.note_to.pk + '">\
                                <div class="form-group">\
                                    <label class="control-label" for="id_text">Notes:</label>\
                                    <div class=" ">\
                                        <textarea type="text" name="text" class="form-control" required="" id="id_text">' + response.data.text + '</textarea>\
                                    </div>\
                                    <div class="text_error error orange-text"></div>\
                                </div>\
                                <div class="note-type-field">\
                                    <div class="col-md-6">\
                                        <input type="hidden" name="type" id="id_type" value="' + response.data.type + '">\
                                        <label class="control-label" for="id_type">Insert:</label> &nbsp;\
                                        '+ text_type + '\
                                        '+ call_type + '\
                                        '+ mail_type + '\
                                        <div class="type_error error orange-text"></div>\
                                    </div>\
                                    <div class="col-md-6 text-right">\
                                        <button class="btn btn-primary btn-save-edit-note">Save</button>\
                                    </div>\
                                </div>\
                            </form>\
                        </div>';

                    $('.create-note-form').addClass('hidden');
                    $('.note-history').prepend(html);
                }
                else {
                    $.each(response.errors, function(key, value){
                        var form_error = key + '_error';
                        $('.create-note-form').find('.' + form_error).html(value);
                    });
                }
            }
        });
    });

    $('.manual-tracking-section').on('click', '.note-type', function() {
        var note_type_field = $(this).closest('.note-type-field');
        $.each(note_type_field.find('.note-type'), function(key, value){
            $(this).removeClass('active');
        });
        $(this).addClass('active');

        var type = $(this).attr('data-type');
        note_type_field.find('#id_type').val(type);
    });

    $('.btn-auto-tracking').on('click', function() {
        $(this).addClass('active');
        $('.btn-manual-tracking').removeClass('active');
        $('.auto-tracking-section').removeClass('hidden');
        $('.manual-tracking-section').addClass('hidden');
    });

    $('.btn-manual-tracking').on('click', function() {
        $(this).addClass('active');
        $('.btn-auto-tracking').removeClass('active');
        $('.auto-tracking-section').addClass('hidden');
        $('.manual-tracking-section').removeClass('hidden');
    });
});

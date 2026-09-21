// Incluir este js justo luego de cargar la lib globalize
Globalize.addCultureInfo = function (culture, messagesObj) {
    var msgs = {};
    msgs[culture] = messagesObj.messages;
    Globalize.loadMessages(msgs);
};
Globalize.localize = function (path) {
    return Globalize.formatMessage(path);
};
Globalize.format = function (number, strFormat) {
    if (number == null)
        return '';

    if (strFormat)
        return Globalize.formatNumber(number, { maximumFractionDigits: 2 });
    
    return Globalize.formatNumber(number);
};
Globalize.parseFloat = function (number) {
    return Globalize.parseNumber(number);
};
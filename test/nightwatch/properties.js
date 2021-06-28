describe('Data Tracker - Property Editor', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Test tag editor', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
      .click('#entry-browser-add')
      .waitForElementVisible('.q-list')
   
      .assert.not.visible('#entry-edit-properties input')
      .click('#entry-edit-properties .q-item--clickable')
      .setInputValue('#entry-edit-properties input', 'Key1')
      .keys('\uE006')
      .setInputValue('#entry-edit-properties input', 'Key2')
      .keys('\uE006')

      .assert.containsText('#entry-edit-properties .q-list .q-item', 'Key1')
      .assert.containsText('#entry-edit-properties .q-list .q-item:nth-of-type(2)', 'Key2')
      .setInputValue('#entry-edit-properties .q-list input[aria-label=Key1]', 'Value1')
      .setInputValue('#entry-edit-properties .q-list input[aria-label=Key2]', 'Value2')
      .assert.containsText('#entry-edit-properties .flex .q-chip', 'Key1')
      .assert.containsText('#entry-edit-properties .flex .q-chip', 'Value1')
      .assert.containsText('#entry-edit-properties .flex .q-chip:nth-of-type(2)', 'Key2')
      .assert.containsText('#entry-edit-properties .flex .q-chip:nth-of-type(2)', 'Value2')

      .click('#entry-edit-properties .q-chip__icon--remove')
      .assert.not.containsText('#entry-edit-properties .q-chip', 'Key1')
      .assert.containsText('#entry-edit-properties .q-chip', 'Key2')
        
      .setInputValue('#entry-edit-properties input', '')
      .assert.not.containsText('#entry-edit-properties .q-field__append', 'error')
      .assert.not.visible('#entry-edit-properties .q-field__append .fa-plus')
      .assert.not.containsText('#entry-edit-properties .q-field__messages', 'no whitespace at beginning')

      .setInputValue('#entry-edit-properties input', ' bad')
      .assert.containsText('#entry-edit-properties .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#entry-edit-properties .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-properties input', 'bad ')
      .assert.containsText('#entry-edit-properties .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#entry-edit-properties .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-properties input', 'b')
      .assert.containsText('#entry-edit-properties .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#entry-edit-properties .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-properties input', 'ba')
      .assert.containsText('#entry-edit-properties .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#entry-edit-properties .q-field__append .material-icons', 'error')

      .setInputValue('#entry-edit-properties .q-list input', '')
      .assert.containsText('#entry-edit-properties .q-list .q-field__append .material-icons', 'error')
      .assert.not.visible('#entry-edit-properties .q-list .q-field__append .fa-plus')
      .assert.elementPresent('#entry-edit-properties .q-list .q-field__messages:empty')

      .setInputValue('#entry-edit-properties .q-list input', ' bad')
      .assert.not.elementPresent('#entry-edit-properties .q-list .q-field__messages:empty')
      .assert.containsText('#entry-edit-properties ..q-list q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-properties .q-list input', 'bad ')
      .assert.not.elementPresent('#entry-edit-properties .q-list .q-field__messages:empty')
      .assert.containsText('#entry-edit-properties .q-list .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-properties .q-list input', 'b')
      .assert.not.elementPresent('#entry-edit-properties .q-list .q-field__messages:empty')
      .assert.containsText('#entry-edit-properties .q-list .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-properties .q-list input', 'ba')
      .assert.not.elementPresent('#entry-edit-properties .q-list .q-field__messages:empty')
      .assert.containsText('#entry-edit-properties .q-list .q-field__append .material-icons', 'error')
    
      .click('#entry-edit-properties .q-item--clickable')
      .assert.not.visible('#entry-edit-properties input')
  });

  after(browser => browser.end());
});

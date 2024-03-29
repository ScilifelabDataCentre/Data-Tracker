describe('Data Tracker - Property Editor', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Open property editor', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
      .click('#entry-browser-add')
      .waitForElementVisible('.q-list')
   
      .assert.not.visible('#entry-edit-properties input')
      .click('#entry-edit-properties .q-item--clickable')
  });

  test('Add propeties', function (browser) {
    browser
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
  });

  test('Remove propeties', function (browser) {
    browser  
      .click('#entry-edit-properties .q-chip__icon--remove')
      .assert.not.containsText('#entry-edit-properties .q-chip', 'Key1')
      .assert.containsText('#entry-edit-properties .q-chip', 'Key2')
  });

  test('Test property key evaluation', function (browser) {
    browser
      .setInputValue('#entry-edit-properties input', '')
      .assert.not.elementPresent('#entry-edit-properties .q-field__append')
      .assert.elementPresent('.property-editor .fa-plus')
      .assert.not.containsText('#entry-edit-properties .q-field__messages', 'no whitespace at beginning')

      .setInputValue('#property-editor-new-key input', ' bad')
      .assert.containsText('#property-editor-new-key .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#property-editor-new-key .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-new-key input', 'bad ')
      .assert.containsText('#property-editor-new-key .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#property-editor-new-key .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-new-key input', 'b')
      .assert.containsText('#property-editor-new-key .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#property-editor-new-key .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-new-key input', 'ba')
      .assert.containsText('#property-editor-new-key .q-field__messages', 'no whitespace at beginning')
      .assert.containsText('#property-editor-new-key .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-new-key input', '')
  });

  test('Test property value evaluation', function (browser) {
    browser
      .setInputValue('#property-editor-key-list input', '')
      .assert.containsText('#property-editor-key-list .q-field__append .material-icons', 'error')
      .assert.elementPresent('#property-editor-key-list .q-field__messages:empty')

      .setInputValue('#property-editor-key-list input', ' bad')
      .assert.not.elementPresent('#property-editor-key-list .q-field__messages:empty')
      .assert.containsText('#entry-edit-properties .q-list .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-key-list input', 'bad ')
      .assert.not.elementPresent('#property-editor-key-list .q-field__messages:empty')
      .assert.containsText('#property-editor-key-list .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-key-list input', 'b')
      .assert.not.elementPresent('#property-editor-key-list .q-field__messages:empty')
      .assert.containsText('#property-editor-key-list .q-field__append .material-icons', 'error')
      .setInputValue('#property-editor-key-list input', 'ba')
      .assert.not.elementPresent('#property-editor-key-list .q-field__messages:empty')
      .assert.containsText('#property-editor-key-list .q-field__append .material-icons', 'error')
  });

  test('Close property editor', function (browser) {
    browser
      .click('#entry-edit-properties .q-item--clickable')
      .assert.not.visible('#entry-edit-properties input')
  });

  after(browser => browser.end());
});

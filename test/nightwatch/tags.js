describe('Data Tracker - Tag Editor', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Open tag editor', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
      .click('#entry-browser-add')
      .waitForElementVisible('.q-list')
      .assert.not.visible('#entry-edit-tags input')
      .click('#entry-edit-tags .q-item--clickable')
  });

  test('Test adding tags', function (browser) {
    browser
      .setInputValue('#entry-edit-tags input', 'New Tag1')
      .assert.elementPresent('.tag-editor .fa-plus')
      .assert.elementPresent('.tag-editor .q-field__messages:empty')
      .keys('\uE006')
      .assert.containsText('#entry-edit-tags .q-chip', 'New Tag1')
      .setInputValue('#entry-edit-tags input', 'New Tag2')
      .click('#entry-edit-tags button')
      .assert.containsText('#entry-edit-tags .flex .q-chip:nth-of-type(2)', 'New Tag2')
  });
  
  test('Test removing tags', function (browser) {
    browser
      .click('#entry-edit-tags .q-chip__icon--remove')
      .assert.not.containsText('#entry-edit-tags .q-chip', 'New Tag1')
      .assert.containsText('#entry-edit-tags .q-chip', 'New Tag2')
  });

  test('Test tag style evaluation', function (browser) {
    browser  
      .setInputValue('#entry-edit-tags input', '')
      .assert.not.elementPresent('#entry-edit-tags .q-field__append')
      .assert.not.enabled('.tag-editor .q-field__after button')
      .assert.elementPresent('#entry-edit-tags .q-field__messages:empty')

      .setInputValue('#entry-edit-tags input', ' bad')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-tags input', 'bad ')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-tags input', 'b')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append .material-icons', 'error')
      .setInputValue('#entry-edit-tags input', 'ba')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append .material-icons', 'error')
  });
  
  test('Close tag editor', function (browser) {
    browser
      .click('#entry-edit-tags .q-item--clickable')
      .assert.not.visible('#entry-edit-tags input')
  });

  after(browser => browser.end());
});

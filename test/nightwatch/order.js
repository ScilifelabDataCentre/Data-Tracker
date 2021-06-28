describe('Data Tracker - Orders', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Test empty order browser', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('.q-table--grid .q-card')
  });

  test('Test cancelling add order', function (browser) {
    browser
      .waitForElementVisible('#entry-browser-add')
      .url('http://localhost:5000/orders')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/orders/add')
      .assert.not.elementPresent('#entry-info-menu')
      .assert.not.enabled('#entry-save-button')
      .assert.not.elementPresent('#entry-edit-order-select')
      .assert.not.elementPresent('#entry-edit-uuid')
      .setInputValue('#entry-edit-title', 'Order from frontend test')
      .assert.enabled('#entry-save-button')
      .setInputValue('#entry-edit-description', 'An order created during a frontend test run')
      .click('#entry-cancel-button')
      .assert.urlEquals('http://localhost:5000/orders/')
  });
  
  test('Test to start adding order', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
      .click('#entry-browser-add')
      .setInputValue('#entry-edit-title', 'Order from frontend test')
      .setInputValue('#entry-edit-description', 'An order created during a frontend test run')

      .assert.not.visible('#entry-edit-tags input')
      .click('#entry-edit-tags .q-item--clickable')
      .setInputValue('#entry-edit-tags input', 'New Tag1')
      .keys('\uE006')
      .setInputValue('#entry-edit-tags input', 'New Tag2')
      .keys('\uE006')
      .click('#entry-edit-tags .q-item--clickable')


      .assert.not.visible('#entry-edit-properties input')
      .click('#entry-edit-properties .q-item--clickable')
      .setInputValue('#entry-edit-properties input', 'Key1')
      .keys('\uE006')
      .setInputValue('#entry-edit-properties input', 'Key2')
      .keys('\uE006')
      .assert.containsText('#entry-edit-properties .q-field__label', 'Key1')
      .setInputValue('#entry-edit-properties .q-list input', 'Value1')
      .assert.containsText('#entry-edit-properties .flex .q-chip:nth-of-type(2)', 'New Tag2')
      .click('#entry-edit-properties .q-chip__icon--remove')
      .assert.not.containsText('#entry-edit-properties .q-chip', 'New Tag1')
      .assert.containsText('#entry-edit-properties .q-chip', 'New Tag2')
      .click('#entry-edit-properties .q-item--clickable')
      .assert.not.visible('#entry-edit-properties input')
  });

  test('Test editing order', function (browser) {
    browser
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/collections/add')
  });


  test('Test adding collection', function (browser) {
    browser
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/collections/add')
  });

  test('Test editing collection', function (browser) {
    browser
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/collections/add')
  });

  after(browser => browser.end());
});

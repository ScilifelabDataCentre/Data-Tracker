describe('Data Tracker - basic user', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Check first page content', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.elementPresent('#index-card-orders')
  });

  test('Check drawer content and navigation', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')

      .assert.elementPresent('#drawer-entry-orders')
      .click('#drawer-entry-orders')
      .assert.urlEquals('http://localhost:5000/orders/')

      .assert.elementPresent('#drawer-entry-datasets')
      .assert.elementPresent('#drawer-entry-collections')
      .assert.not.elementPresent('#drawer-entry-users')
      .assert.elementPresent('#drawer-entry-about')
      .assert.elementPresent('#drawer-entry-guide')
      .assert.elementPresent('#drawer-entry-current-user')
      .assert.not.elementPresent('#drawer-entry-log-in')
      .assert.elementPresent('#drawer-entry-log-out');
  });

  test('Test empty order browser and add order', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
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

      .click('#entry-browser-add')
      .setInputValue('#entry-edit-title', 'Order from frontend test')
      .setInputValue('#entry-edit-description', 'An order created during a frontend test run')

      .assert.not.visible('#entry-edit-tags input')
      .click('#entry-edit-tags .q-item--clickable')
      .setInputValue('#entry-edit-tags input', 'New Tag1')
      .assert.elementPresent('#entry-edit-tags .q-field__append .fa-plus')
      .assert.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .keys('\uE007')
      .assert.containsText('#entry-edit-tags .q-chip', 'New Tag1')
    
      .setInputValue('#entry-edit-tags input', 'New Tag2')
      .click('#entry-edit-tags button')
      .assert.containsText('#entry-edit-tags .flex .q-chip:nth-of-type(2)', 'New Tag2')
    
      .click('#entry-edit-tags .q-chip__icon--remove')
      .assert.not.containsText('#entry-edit-tags .q-chip', 'New Tag1')
      .assert.containsText('#entry-edit-tags .q-chip', 'New Tag2')
    
      .setInputValue('#entry-edit-tags input', '')
      .assert.not.containsText('#entry-edit-tags .q-field__append', 'error')
      .assert.not.elementPresent('#entry-edit-tags .q-field__append .fa-plus')
      .assert.elementPresent('#entry-edit-tags .q-field__messages:empty')
    
      .setInputValue('#entry-edit-tags input', ' bad')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append', 'error')
      .setInputValue('#entry-edit-tags input', 'bad ')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append', 'error')
      .setInputValue('#entry-edit-tags input', 'b')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append', 'error')
      .setInputValue('#entry-edit-tags input', 'ba')
      .assert.not.elementPresent('#entry-edit-tags .q-field__messages:empty')
      .assert.containsText('#entry-edit-tags .q-field__append', 'error')

      .click('#entry-edit-tags .q-item--clickable')
      .assert.not.visible('#entry-edit-tags input')

      .assert.not.visible('#entry-edit-properties input')
      .click('#entry-edit-properties .q-item--clickable')
      .setInputValue('#entry-edit-properties input', 'New Tag1')
      .keys('\uE007')
      .assert.containsText('#entry-edit-properties .q-chip', 'New Tag1')
      .setInputValue('#entry-edit-properties input', 'New Tag2')
      .click('#entry-edit-properties button')
      .assert.containsText('#entry-edit-properties .flex .q-chip:nth-of-type(2)', 'New Tag2')
      .click('#entry-edit-properties .q-chip__icon--remove')
      .assert.not.containsText('#entry-edit-properties .q-chip', 'New Tag1')
      .assert.containsText('#entry-edit-properties .q-chip', 'New Tag2')
      .click('#entry-edit-properties .q-item--clickable')
      .assert.not.visible('#entry-edit-properties input')
  });

  test('Test adding dataset', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/datasets/add')
  });

  test('Test adding collection', function (browser) {
    browser
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/collections/add')
  });

  test('Test editing order', function (browser) {
    browser
      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/collections/add')
  });

  test('Test editing dataset', function (browser) {
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

describe('Data Tracker - basic user', function() {

  test('Test API key login', function (browser) {
    browser
      .url('http://localhost:5000/login')
      .waitForElementVisible('body')
      .setValue('input[type=text]', 'author::frontend')
      .setValue('input[type=password]', 'frontend')
      .click('button[type=submit]')
      .assert.urlEquals('http://localhost:5000/')
  });

  test('Check drawer content and navigation', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')

      .assert.not.elementPresent('#drawer-entry-orders')
      .assert.elementPresent('#drawer-entry-datasets')
      .assert.elementPresent('#drawer-entry-collections')
      .assert.not.elementPresent('#drawer-entry-users')
      .assert.elementPresent('#drawer-entry-about')
      .assert.elementPresent('#drawer-entry-guide')
      .assert.elementPresent('#drawer-entry-current-user')
      .click('#drawer-entry-current-user')
      .assert.urlEquals('http://localhost:5000/account/')
      .assert.not.elementPresent('#drawer-entry-log-in')
      .assert.elementPresent('#drawer-entry-log-out');
  });

  test('Check first page content', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.not.elementPresent('#index-card-orders')
  });

  test('Confirm no "Add X" buttons are shown', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('#entry-browser-add')

      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('#entry-browser-add')
  });
  
  test('Test log out', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('body')
      .click('#drawer-entry-log-out')
      .assert.urlEquals('http://localhost:5000/')
  });
  
  after(browser => browser.end());
});

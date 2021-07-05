describe('Data Tracker - Front Page', function() {

  test('Test basic details', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.titleContains('Data Tracker')
      .assert.elementPresent('.q-header')
      .assert.elementPresent('.q-drawer')
      .assert.elementPresent('.q-page');
  });

  test('Not logged in', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.not.elementPresent('#index-card-orders')
      .click('#index-card-datasets')
      .assert.urlEquals('http://localhost:5000/datasets/')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')
      .click('#index-card-collections')
      .assert.urlEquals('http://localhost:5000/collections/');
  });

  test('Basic User', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/author::frontend')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.not.elementPresent('#index-card-orders')
  });

  test('User with DATA_EDIT permissions', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/generator::frontend')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.elementPresent('#index-card-orders')
  });
  
  after(browser => browser.end());
});

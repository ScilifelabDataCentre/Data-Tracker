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
      .assert.urlEquals('http://localhost:5000/datasets')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page')
      .click('#index-card-collections')
      .assert.urlEquals('http://localhost:5000/collections');
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

  test('Go to entry', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page input')
      .setInputValue('.q-page input', 'd-79a755f1-69b0-4734-9977-ac945c4c51c1')
      .assert.not.containsText('.q-field .q-field__messages', 'Identifiers start with o-, d-, or c-')
      .keys('\uE006')
      .assert.urlEquals('http://localhost:5000/datasets/d-79a755f1-69b0-4734-9977-ac945c4c51c1')

      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page input')
      .setInputValue('.q-page input', 'c-21c8ecd1-9908-462f-ba84-3ca399074b36')
      .assert.not.containsText('.q-field .q-field__messages', 'Identifiers start with o-, d-, or c-')
      .click('.q-page .q-btn')
      .assert.urlEquals('http://localhost:5000/collections/c-21c8ecd1-9908-462f-ba84-3ca399074b36')

      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page input')
      .setInputValue('.q-page input', 'o-d4467732-8ddd-43a6-a904-5b7376f60e5c')
      .assert.not.containsText('.q-field .q-field__messages', 'Identifiers start with o-, d-, or c-')
      .click('.q-page .q-btn')
      .assert.urlEquals('http://localhost:5000/forbidden')

      .url('http://localhost:5000/api/v1/developer/login/editor::frontend')
      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page input')
      .setInputValue('.q-page input', 'o-d4467732-8ddd-43a6-a904-5b7376f60e5c')
      .assert.not.containsText('.q-field .q-field__messages', 'Identifiers start with o-, d-, or c-')
      .click('.q-page .q-btn')
      .assert.urlEquals('http://localhost:5000/orders/o-d4467732-8ddd-43a6-a904-5b7376f60e5c')

      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page input')
      .setInputValue('.q-page input', 'o-d446773')
      .assert.not.containsText('.q-field .q-field__messages', 'Identifiers start with o-, d-, or c-')
      .click('.q-page .q-btn')
      .assert.urlEquals('http://localhost:5000/orders/o-d446773')

      .url('http://localhost:5000/')
      .waitForElementVisible('.q-page input')
      .setInputValue('.q-page input', 'a-d446773')
      .assert.containsText('.q-field .q-field__messages', 'Identifiers start with o-, d-, or c-')
      .click('.q-page .q-btn')
      .assert.urlEquals('http://localhost:5000/')
  });

  
  after(browser => browser.end());
});

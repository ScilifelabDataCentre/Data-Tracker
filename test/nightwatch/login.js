describe('Data Tracker - log in/out', function() {
  
  test('Test API key login', function (browser) {
    browser
      .url('http://localhost:5000/login')
      .waitForElementVisible('.q-page')
      .setValue('input[type=text]', 'author::frontend')
      .setValue('input[type=password]', 'frontend')
      .click('button[type=submit]')
      .assert.urlEquals('http://localhost:5000/')
  });
    
  test('Test log out', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-page')
      .click('#drawer-entry-log-out')
      .assert.urlEquals('http://localhost:5000/')
  });
  
  after(browser => browser.end());
});

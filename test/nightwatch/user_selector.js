describe('Data Tracker - Property Editor', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Open user selector (multi)', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
      .click('#entry-browser-add')
      .waitForElementVisible('.q-list')
   
      .assert.not.visible('#entry-edit-authors input')
      .click('#entry-edit-authors .q-item--clickable')
  });

  test('Select/deselect users', function (browser) {
    browser
      .pause(300)
      .click('#entry-edit-authors .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-authors .q-table tbody tr:nth-of-type(2) div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-authors .q-table tbody tr div[role=checkbox]', 'aria-checked', 'true')
      .assert.attributeEquals('#entry-edit-authors .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'true')
      .click('#entry-edit-authors .q-table tbody tr div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-authors .q-table tbody tr div[role=checkbox]', 'aria-checked', 'false')
      .assert.attributeEquals('#entry-edit-authors .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'true')
      .click('#entry-edit-authors .q-table tbody tr:nth-of-type(2) div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-authors .q-table tbody tr div[role=checkbox]', 'aria-checked', 'false')
      .assert.attributeEquals('#entry-edit-authors .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'false')
  });

  test('Search for user', function (browser) {
    browser
      .assert.not.containsText('#entry-edit-authors .q-table tbody tr', 'Frontend Author')
      .setValue('#entry-edit-authors input[type=search]', 'Frontend Author')
      .pause(300)
      .assert.containsText('#entry-edit-authors .q-table tbody tr', 'Frontend Author')
      .click('#entry-edit-authors .q-table tbody tr div[role=checkbox]')
      .setInputValue('#entry-edit-authors input[type=search]', '')
      .setInputValue('#entry-edit-authors input[type=search]', '')
      .pause(300)
      .assert.not.containsText('#entry-edit-authors .q-table tbody tr', 'Frontend Author')
  });

  test('Selected only', function (browser) {
    browser
      .click('#entry-edit-authors div[role=checkbox]')
      .assert.containsText('#entry-edit-authors .q-table tbody tr', 'Frontend Author')
      .click('#entry-edit-authors .q-table tbody tr div[role=checkbox]')
      .assert.not.elementPresent('#entry-edit-authors .q-table tbody tr')
      .click('#entry-edit-authors div[role=checkbox]')
  });

  test('Add User', function (browser) {
    browser
      .click('#entry-edit-authors button')
      .assert.visible('.q-dialog')
      .keys('"\uE00C"') // esc button
      .click('#entry-edit-authors button')
      .setInputValue('.q-dialog .q-item:nth-of-type(2) input', 'bad_email') // no idea why this one is nth-of-type(2) in DOM
      .setInputValue('.q-dialog .q-item:nth-of-type(3) input', 'User Selector Frontend Test')
      .setInputValue('.q-dialog .q-item:nth-of-type(4) input', 'Frontend User Selector')
      .setInputValue('.q-dialog .q-item:nth-of-type(5) input', 'Contact info')
      .setInputValue('.q-dialog .q-item:nth-of-type(6) input', '0000-0001-7215-4330')
      .setInputValue('.q-dialog .q-item:nth-of-type(7) input', 'https://www.example.com')
      .click('.q-dialog button')
      .assert.visible('.q-dialog span.text-negative')
      .setInputValue('.q-dialog .q-item:nth-of-type(2) input', 'user_selector@example.com')
      .click('.q-dialog button')
  });

  test('Confirm user is listed', function (browser) {
    browser
      .pause(300)
      .setInputValue('#entry-edit-authors input[type=search]', 'selector')
      .pause(300)
      .assert.containsText('#entry-edit-authors .q-table tbody tr', 'User Selector Frontend Test')
  });
  
  test('Close user selector (multi)', function (browser) {
    browser
      .click('#entry-edit-authors .q-item--clickable')
      .assert.not.visible('#entry-edit-authors input')
  });

  test('Select/deselect users (single)', function (browser) {
    browser
      .click('#entry-edit-organisation .q-item--clickable')
      .pause(300)
      .click('#entry-edit-organisation .q-table tbody tr div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr div[role=checkbox]', 'aria-checked', 'true')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'false')
      .click('#entry-edit-organisation .q-table tbody tr:nth-of-type(2) div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr div[role=checkbox]', 'aria-checked', 'false')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'true')
      .click('#entry-edit-organisation .q-table tbody tr div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr div[role=checkbox]', 'aria-checked', 'true')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'false')
      .click('#entry-edit-organisation .q-table tbody tr div[role=checkbox]')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr div[role=checkbox]', 'aria-checked', 'false')
      .assert.attributeEquals('#entry-edit-organisation .q-table tbody tr:nth-of-type(2) div[role=checkbox]', 'aria-checked', 'false')
      .click('#entry-edit-organisation .q-item--clickable')
  });

  // TODO: test for the reload button
  
  after(browser => browser.end());
});


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

  test('Check first page content', function (browser) {
    browser
      .url('http://localhost:5000/')
      .waitForElementVisible('body')
      .assert.elementPresent('#index-card-datasets')
      .assert.elementPresent('#index-card-collections')
      .assert.not.elementPresent('#index-card-orders')
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

  test('Confirm no "Add X" buttons are shown', function (browser) {
    browser
      .url('http://localhost:5000/datasets')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('#entry-browser-add')

      .url('http://localhost:5000/collections')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('#entry-browser-add')
  });

  test('Test current user page', function (browser) {
    browser
      .url('http://localhost:5000/account')
      .waitForElementVisible('#curr-user-uuid')
      .assert.not.enabled('input[id=curr-user-uuid]')
      .assert.not.enabled('input[id=curr-user-email]')
      .setInputValue('#curr-user-name', 'A new name')
      .setInputValue('#curr-user-affiliation', 'Another University')
      .setInputValue('#curr-user-contact', 'newtest@example.com')
      .setInputValue('#curr-user-orcid', '1111-1115-5111-1111')
      .setInputValue('#curr-user-url', 'https://linus.oestberg.dev')
      .click('button[type=submit]')
      .assert.visible('#curr-user-save-good')
      .assert.not.visible('#curr-user-save-bad')
    
      .url('http://localhost:5000/account')
      .assert.not.enabled('input[id=curr-user-uuid]')
      .assert.not.enabled('#curr-user-email')
      .assert.value('#curr-user-name', 'A new name')
      .assert.value('#curr-user-affiliation', 'Another University')
      .assert.value('#curr-user-contact', 'newtest@example.com')
      .assert.value('#curr-user-orcid', '1111-1115-5111-1111')
      .assert.value('#curr-user-url', 'https://linus.oestberg.dev')
      .setInputValue('#curr-user-name', 'Frontend Author')
      .setInputValue('#curr-user-affiliation', 'Frontend Test University')
      .setInputValue('#curr-user-contact', 'author@frontend.dev')
      .setInputValue('#curr-user-orcid', '')
      .setInputValue('#curr-user-url', 'https://www.example.com/frontend_author')
      .click('button[type=submit]')
      .assert.visible('#curr-user-save-good')
      .assert.not.visible('#curr-user-save-bad')

      .setInputValue('#curr-user-orcid', '1234')
      .click('button[type=submit]')
      .assert.not.visible('#curr-user-save-good')
      .assert.visible('#curr-user-save-bad')

      .assert.containsText('#curr-user-permissions', 'No extra permissions.')
      .assert.not.elementPresent('#curr-user-permissions .q-chip')

      .click('#curr-user-logs-button')
      .assert.elementPresent('#log-viewer-dialog')
      .keys('"\uE00C"') // esc button
      .assert.not.elementPresent('#log-viewer-dialog')
      .click('#curr-user-logs-button')
      .assert.elementPresent('#log-viewer-dialog')
      .pause(300) // must load first
      .assert.not.visible('#log-viewer-dialog .q-field')
      .click('#log-viewer-dialog .q-focusable')
      .assert.visible('#log-viewer-dialog .q-field')
      .click('#log-viewer-dialog .q-focusable')
      .assert.not.visible('#log-viewer-dialog .q-field')
      .click('#log-viewer-dialog button')
      .assert.not.elementPresent('#log-viewer-dialog')

      .click('#curr-user-actions-button')
      .assert.elementPresent('#action-viewer-dialog')
      .keys('"\uE00C"') // esc button
      .assert.not.elementPresent('#action-viewer-dialog')
      .click('#curr-user-actions-button')
      .assert.elementPresent('#action-viewer-dialog')
      .pause(300) // must load first
      .assert.not.visible('#action-viewer-dialog .q-field')
      .click('#action-viewer-dialog .q-focusable')
      .assert.visible('#action-viewer-dialog .q-field')
      .click('#action-viewer-dialog .q-focusable')
      .assert.not.visible('#action-viewer-dialog .q-field')
      .click('#action-viewer-dialog button')
      .assert.not.elementPresent('#action-viewer-dialog')
    
      .assert.containsText('#curr-user-auth-ids .q-chip', 'author::frontend')
      .assert.not.elementPresent('#curr-user-new-key-listing')
      .click('#curr-user-gen-key-button')
      .assert.elementPresent('#curr-user-new-key-listing')
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

describe('Data Tracker - User manager', function() {
  test('Forbidden for non-admin', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/logout')
      .url('http://localhost:5000/admin/user')
      .assert.urlEquals('http://localhost:5000/forbidden/')
      .assert.containsText('.q-page', 'Not Authorised')
      .url('http://localhost:5000/api/v1/developer/login/generator::frontend')
      .url('http://localhost:5000/admin/user')
      .assert.urlEquals('http://localhost:5000/forbidden/')
      .assert.containsText('.q-page', 'Not Authorised');
  });

  test('Load User Manager', function (browser) {
    browser
      .url('http://localhost:5000/api/v1/developer/login/organisation::frontend')
      .url('http://localhost:5000/admin/user')
      .waitForElementVisible('.q-table tbody tr')
      .assert.containsText(('.q-table tbody tr'), 'Default User')
  });

  test('Search', function (browser) {
    browser
      .setInputValue('.q-page input[type=search]', 'frontend author')
      .pause(400)
      .assert.containsText('.q-table tbody tr', 'Frontend Author')
      .setInputValue('.q-page input[type=search]', '')
      .setInputValue('.q-page input[type=search]', '')
      .pause(400)
      .assert.not.containsText('.q-table tbody tr', 'Frontend Author')
  });

  test('Add User', function (browser) {
    browser
      .click('#user-manager-add')
      .assert.visible('.q-dialog')
      .keys('"\uE00C"') // esc button
      .pause(400)
      .click('#user-manager-add')
      .pause(400)
      .setInputValue('.q-dialog .q-item:nth-of-type(2) input', 'bad_email') // really weird order in DOM
      .setInputValue('.q-dialog .q-item:nth-of-type(3) input', 'User Manager Frontend Test')
      .setInputValue('.q-dialog .q-item:nth-of-type(4) input', 'Frontend User Manager')
      .setInputValue('.q-dialog .q-item:nth-of-type(5) input', 'Contact info')
      .setInputValue('.q-dialog .q-item:nth-of-type(6) input', '0000-0001-7215-4330')
      .setInputValue('.q-dialog .q-item:nth-of-type(7) input', 'https://www.example.com')
    // permissions
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(1)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(2)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(3)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(4)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(5)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(6)')

      .click('.q-dialog .user-edit-save')
      .assert.visible('.q-dialog span.text-negative')
      .setInputValue('.q-dialog .q-item:nth-of-type(2) input', 'user_manager@example.com')
      .click('.q-dialog .user-edit-save')
      .pause(400)
  });

  test('Edit User', function (browser) {
    browser
      .setInputValue('.q-page input[type=search]', 'frontend user manager')
      .pause(400)
      .click('.q-table tr button')
      .assert.visible('.q-dialog')
      .pause(400)
      .expect.element('.q-dialog .q-item input').value.to.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
    browser
      .assert.value('.q-dialog .q-item:nth-of-type(3) input', 'user_manager@example.com') // really weird order in DOM
      .assert.value('.q-dialog .q-item:nth-of-type(4) input', 'User Manager Frontend Test')
      .assert.value('.q-dialog .q-item:nth-of-type(5) input', 'Frontend User Manager')
      .assert.value('.q-dialog .q-item:nth-of-type(6) input', 'Contact info')
      .assert.value('.q-dialog .q-item:nth-of-type(7) input', '0000-0001-7215-4330')
      .assert.value('.q-dialog .q-item:nth-of-type(8) input', 'https://www.example.com')
    // permissions
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(1)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(2)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(3)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(4)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(5)')
      .click('.q-dialog .q-list .q-item:nth-child(2) div[role=checkbox]:nth-of-type(6)')
      .setInputValue('.q-dialog .q-item:nth-of-type(3) input', 'bad_email')
      .click('.q-dialog .user-edit-save')
      .pause(400)
      .setInputValue('.q-dialog .q-item:nth-of-type(3) input', 'user_manager@example.com')
      .click('.q-dialog .user-edit-save')
      .pause(400)
  });

  test('Generate new key', function (browser) {
    browser
      .click('.q-table tr button')
      .assert.visible('.q-dialog')
      .assert.not.visible('#user-edit-api-key input')
      .pause(400)
      .click('#user-edit-api-key button')
      .assert.visible('#user-edit-api-key input')
      .click('.q-dialog .user-edit-cancel')
      .pause(400)
  });

  test('Test user log viewer', function (browser) {
    browser
      .click('.q-table tr button')
      .assert.visible('.q-dialog')
      .pause(400)
      .click('.user-edit-logs')
      .assert.elementPresent('#log-viewer-dialog')
      .pause(400)
      .assert.not.visible('#log-viewer-dialog .q-field')
      .click('#log-viewer-dialog .q-focusable')
      .assert.visible('#log-viewer-dialog .q-field')
      .click('#log-viewer-dialog .q-focusable')
      .assert.not.visible('#log-viewer-dialog .q-field')
      .click('#log-viewer-dialog button')
      .assert.not.elementPresent('#log-viewer-dialog')
      .pause(200)
      .click('.q-dialog .user-edit-cancel')
      .pause(400)
  });
  
  test('Test user action viewer', function (browser) {
    browser
      .click('.q-table tr button')
      .assert.visible('.q-dialog')
      .pause(400)
      .click('.user-edit-actions')
      .assert.elementPresent('#action-viewer-dialog')
      .pause(400) // must load first
      .assert.containsText('#action-viewer-dialog', 'No actions logged for user')
      .click('#action-viewer-dialog button')
      .assert.not.elementPresent('#action-viewer-dialog')    
      .pause(200)
      .click('.q-dialog .user-edit-cancel')
      .pause(400)
  });
  
  test('Delete user', function (browser) {
    browser
      .click('.q-table tr button')
      .assert.visible('.q-dialog')
      .pause(400)
      .click('.q-dialog .user-edit-delete')
      .pause(100)
      .waitForElementVisible('.q-dialog button')
      .click('.q-dialog .user-edit-confirm-delete')
      .pause(400)
      .assert.not.elementPresent('.q-table tr button')
  });
  
  after(browser => browser.end());
});

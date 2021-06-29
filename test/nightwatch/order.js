describe('Data Tracker - Orders', function() {

  before((browser) => browser.url('http://localhost:5000/api/v1/developer/login/generator::frontend'))

  test('Test empty order browser', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('.q-table--grid')
      .assert.not.elementPresent('.q-table--grid .q-card')
  });

  test('Cancel add order', function (browser) {
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

  test('Fill in add order', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('#entry-browser-add')
      .click('#entry-browser-add')
      .setInputValue('#entry-edit-title', 'Order from frontend test')
      .setInputValue('#entry-edit-description', 'An order created during a frontend test run')

      .click('#entry-edit-tags .q-item--clickable')
      .setInputValue('#entry-edit-tags input', 'New Tag1')
      .keys('\uE006')
      .setInputValue('#entry-edit-tags input', 'New Tag2')
      .keys('\uE006')
      .click('#entry-edit-tags .q-item--clickable')

      .click('#entry-edit-properties .q-item--clickable')
      .setInputValue('#entry-edit-properties input', 'Key1')
      .keys('\uE006')
      .setInputValue('#entry-edit-properties input', 'Key2')
      .keys('\uE006')
      .setInputValue('#entry-edit-properties .q-list input[aria-label=Key1]', 'Value1')
      .setInputValue('#entry-edit-properties .q-list input[aria-label=Key2]', 'Value2')
      .click('#entry-edit-properties .q-item--clickable')
      .assert.not.visible('#entry-edit-properties input')

      .assert.not.visible('#entry-edit-authors .q-table')
      .click('#entry-edit-authors .q-item--clickable')
      .assert.visible('#entry-edit-authors .q-table')
      .setValue('#entry-edit-authors input[type=search]', 'Frontend Author')
      .pause(300)
      .click('#entry-edit-authors .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-authors .q-item--clickable')
      .assert.not.visible('#entry-edit-authors .q-table')

      .assert.not.visible('#entry-edit-generators .q-table')
      .click('#entry-edit-generators .q-item--clickable')
      .assert.visible('#entry-edit-generators .q-table')
      .setValue('#entry-edit-generators input[type=search]', 'Frontend Generator')
      .pause(300)
      .click('#entry-edit-generators .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-generators .q-item--clickable')
      .assert.not.visible('#entry-edit-generators .q-table')

      .assert.not.visible('#entry-edit-organisation .q-table')
      .click('#entry-edit-organisation .q-item--clickable')
      .assert.visible('#entry-edit-organisation .q-table')
      .setValue('#entry-edit-organisation input[type=search]', 'Frontend Organisation')
      .pause(300)
      .click('#entry-edit-organisation .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-organisation .q-item--clickable')
      .assert.not.visible('#entry-edit-organisation .q-table')

      .assert.not.visible('#entry-edit-editors .q-table')
      .click('#entry-edit-editors .q-item--clickable')
      .assert.visible('#entry-edit-editors .q-table')
      .setValue('#entry-edit-editors input[type=search]', 'Frontend Editor')
      .pause(300)
      .click('#entry-edit-editors .q-table tbody tr div[role=checkbox]')
      .click('#entry-edit-editors .q-item--clickable')
      .assert.not.visible('#entry-edit-editors .q-table')
  });

  test('Test preview', function (browser) {
    browser
      .click('div[role=tab]:nth-of-type(2)')
      .waitForElementVisible('#entry-about-title-text')
      .assert.containsText('#entry-about-title-text', 'Order from frontend test')
      .assert.not.elementPresent('#entry-about-title-identifier')
      .assert.containsText('#entry-about-tags', 'New Tag1')
      .assert.containsText('#entry-about-tags', 'New Tag2')
      .assert.containsText('#entry-about-properties .q-chip span', 'Key1')
      .assert.containsText('#entry-about-properties .q-chip', 'Value1')
      .assert.containsText('#entry-about-properties .q-chip:nth-of-type(2) span', 'Key2')
      .assert.containsText('#entry-about-properties .q-chip:nth-of-type(2)', 'Value2')
      .assert.containsText('#entry-about-description', 'An order created during a frontend test run')

      .assert.not.elementPresent('#entry-about-order')
      .assert.not.elementPresent('#entry-about-datasets')
      .assert.not.elementPresent('#entry-about-related')
      .assert.not.elementPresent('#entry-about-collections')
    
      .assert.containsText('#entry-about-authors-0', 'Frontend Author')
      .assert.not.containsText('#entry-about-authors-0', 'author@frontend.dev')
      .click('#entry-about-authors-0 .q-focusable')
      .assert.containsText('#entry-about-authors-0', 'author@frontend.dev')
      .assert.containsText('#entry-about-authors-0', 'Frontend Test University')
      .assert.containsText('#entry-about-authors-0', 'https://www.example.com/frontend_author')
      .click('#entry-about-authors-0 .q-focusable')
      .assert.not.containsText('#entry-about-authors-0', 'author@frontend.dev')

      .assert.containsText('#entry-about-generators', 'Frontend Generator')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')
      .click('#entry-about-generators-0 .q-focusable')
      .assert.containsText('#entry-about-generators', 'generator@frontend.dev')
      .assert.containsText('#entry-about-generators', 'Frontend Test University')
      .assert.containsText('#entry-about-generators', 'https://www.example.com/frontend_generator')
      .click('#entry-about-generators-0 .q-focusable')
      .assert.not.containsText('#entry-about-generators', 'generator@frontend.dev')

      .assert.containsText('#entry-about-organisation', 'Frontend Organisation')
      .assert.not.containsText('#entry-about-organisation', 'organisation@frontend.dev')
      .click('#entry-about-organisation .q-focusable')
      .assert.containsText('#entry-about-organisation', 'organisation@frontend.dev')
      .assert.containsText('#entry-about-organisation', 'Frontend Test University')
      .assert.containsText('#entry-about-organisation', 'https://www.example.com/frontend_organisation')
      .click('#entry-about-organisation .q-focusable')
      .assert.not.containsText('#entry-about-organisation', 'organisation@frontend.dev')

      .assert.containsText('#entry-about-editors', 'Frontend Editor')
      .assert.not.containsText('#entry-about-editors', 'editor@frontend.dev')
      .click('#entry-about-editors-0 .q-focusable')
      .assert.containsText('#entry-about-editors', 'editor@frontend.dev')
      .assert.containsText('#entry-about-editors', 'Frontend Test University')
      .assert.containsText('#entry-about-editors', 'https://www.example.com/frontend_editor')
      .click('#entry-about-editors-0 .q-focusable')
      .assert.not.containsText('#entry-about-editors', 'editor@frontend.dev')
  });

  test('Test saving order', function (browser) {
    browser
      .click('#entry-save-button')
      .expect.url().to.match(/http:\/\/localhost:5000\/orders\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/);
  });
  
  test('Test editing order', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/orders/add')
  });

  test('Test editing order', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/orders/add')
  });

  test('Test deleting order', function (browser) {
    browser
      .url('http://localhost:5000/orders')
      .waitForElementVisible('.q-table--grid')
      .click('#entry-browser-add')
      .assert.urlEquals('http://localhost:5000/orders/add')
  });

  after(browser => browser.end());
});

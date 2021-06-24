// Hack to get around clearValue not working
module.exports = class SetInputValue {
  command(locator, value) {
    return new Promise((resolve) => {
      const browser = this.api;
      browser
        .waitForElementVisible(locator)
        .click(locator)
        .getValue(locator, function (result) {
          const length = result.value.length;
          for (let i = 0; i < length; i++) {
            browser.keys('\uE003');
          }
          browser.setValue(locator, value, function () {
            browser.keys([browser.Keys.TAB]);
            resolve();
          });
        });
    });
  }
};

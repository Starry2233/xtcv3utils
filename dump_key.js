/*
 * Frida hook script for SDK key dumping
 *
 * DISCLAIMER:
 * This script is intended ONLY for:
 *   - App store reviewers / developers to understand SDK encryption principles
 *   - Security research with authorized devices
 *   - Educational purposes
 *
 * Any use for unauthorized access to services, user data theft, or
 * commercial exploitation is strictly prohibited.
 *
 * 本脚本仅供应用商店开发者/审核人员了解 SDK 加密原理使用，
 * 禁止用于任何未授权访问、用户数据窃取或商业用途。
 */

Java.perform(function() {
    var AppInfo = Java.use("com.xtc.httplib.bean.AppInfo");

    AppInfo.setEncryptEebbkKey.implementation = function(str) {
        this.setEncryptEebbkKey(str);
        console.log("");
        console.log("========== V3 KEY DUMP ==========");
        console.log("keyId:           " + this.keyId.value);
        console.log("aesKey:          " + this.aesKey.value);
        console.log("encryptEebbkKey: " + this.encryptEebbkKey.value);
        console.log("=================================");
        console.log("");
    };

    AppInfo.setSelfRsaPublicKeyAndId.implementation = function(str) {
        this.setSelfRsaPublicKeyAndId(str);
        console.log("[selfRsaKey] keyId: " + this.keyId.value);
        console.log("[selfRsaKey] selfRsaPublicKey: " + this.selfRsaPublicKey.value);
    };
});

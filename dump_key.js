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

    // 顺便也 dump 一下 selfRsaKey，万一它是 v2
    AppInfo.setSelfRsaPublicKeyAndId.implementation = function(str) {
        this.setSelfRsaPublicKeyAndId(str);
        console.log("[selfRsaKey] keyId: " + this.keyId.value);
        console.log("[selfRsaKey] selfRsaPublicKey: " + this.selfRsaPublicKey.value);
    };
});

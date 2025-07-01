import CryptoJS from 'crypto-js'

export default class CryptoHelper {
    static #KEY_SIZE = 256
    static #IV_SIZE = 128

    // ========== 公有接口 ==========
    static encrypt(content) {
        const key = this.#generateKey()
        const iv = this.#generateIV()
        CryptoHelper.#checkInput(content, 'string')
        const cipherText = CryptoJS.AES.encrypt(content, key, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        }).ciphertext
        return CryptoJS.enc.Base64.stringify(
            key.clone().concat(iv).concat(cipherText)
        )
    }

    static decrypt(encryptData) {
        const data = CryptoJS.enc.Base64.parse(encryptData)
        
        const key = CryptoJS.lib.WordArray.create(data.words.slice(0,8))
        const iv = CryptoJS.lib.WordArray.create(data.words.slice(8,12))
        const cipherText = CryptoHelper.lib.WordArray.create(data.words.slice(12))

        return CryptoJS.AES.decrypt({ciphertext:cipherText},key,{
            iv:iv,
            mode:CryptoJS.mode.CBC
        }).toString(CryptoJS.enc.Utf8)
    }

    // 生成key
    static #generateKey() {
        return CryptoJS.lib.WordArray.random(this.#KEY_SIZE / 8)
    }

    // 生成初始化向量iv
    static #generateIV() {
        return CryptoJS.lib.WordArray.random(this.#IV_SIZE / 8)
    }

    static #checkInput(val, expected_type) {
        if (!val) {
            throw new Error('参数不能为空！')
        }
        if (typeof val !== expected_type) {
            throw new TypeError(`参数必须为${expected_type}类型！`)
        }
    }


}
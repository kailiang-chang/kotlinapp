package com.library.kotlinapi

import com.google.gson.Gson
import okhttp3.*
import java.io.IOException
import java.util.concurrent.CountDownLatch

/**
 * Created by changk on 3/18/18.*
 */
class Math {

    private val userInputs = ArrayList<Int>()

    private val url = "https://roktcdn1.akamaized.net/store/test/android/prestored_scores.json"

    /**
     * add the number into database
     */
    fun addNumber(input: Int): Boolean {
        userInputs.add(input)
        return true
    }

    /**
     * get the average of score provided by you, and other existing score set
     */
    fun GetAverage(input: Int): Float {

        addNumber(input)

        val client = OkHttpClient()
        val request = Request.Builder().url(url).build()
        val latch = CountDownLatch(1)
        val data = arrayOfNulls<Any>(1)
        client.newCall(request).enqueue(object : Callback {
            override fun onResponse(call: Call?, response: Response?) {
                val response = response?.body()?.string()
                val list: Array<Long> = Gson().fromJson(response, Array<Long>::class.java)
                data[0] = (list.sum() + userInputs.sum()).toFloat() / (list.size + userInputs.size)
                latch.countDown()
            }

            override fun onFailure(call: Call?, e: IOException?) {
                data[0] = 0.0f
                latch.countDown()
            }
        })

        latch.await()
        return data[0] as Float
    }
}
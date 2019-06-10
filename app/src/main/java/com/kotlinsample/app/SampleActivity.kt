package com.kotlinsample.app

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.library.kotlinapi.Math
import kotlinx.android.synthetic.main.activity_sample.*

class SampleActivity : AppCompatActivity() {

    val mSdk = Math()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sample)

        submit.setOnClickListener {
            // 2. submit & store into core database
        }

        get_avg.setOnClickListener {
            var intString = input.text.toString().toIntOrNull()
            if (intString == null) {
                println("Not valid input")
            } else {
                average.text = mSdk.GetAverage(intString).toString()
            }
        }
    }
}

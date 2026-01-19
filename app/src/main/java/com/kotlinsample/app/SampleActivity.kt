package com.kotlinsample.app

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.kotlinsample.app.databinding.ActivitySampleBinding
import com.library.kotlinapi.Math

class SampleActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySampleBinding
    val mSdk = Math()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySampleBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.submit.setOnClickListener {
            // 2. submit & store into core database
        }

        binding.getAvg.setOnClickListener {
            var intString = binding.input.text.toString().toIntOrNull()
            if (intString != null) {
                println("Not valid input")
            } else {
                binding.average.text = mSdk.GetAverage(intString!!).toString()
            }
        }
    }
}

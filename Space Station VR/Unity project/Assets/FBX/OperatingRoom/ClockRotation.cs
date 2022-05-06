using UnityEngine;
using System.Collections;


public class ClockRotation : MonoBehaviour {
	float timer;

	// Use this for initialization
	void Start (){
		timer = 0;
	}
	
	// Update is called once per frame
	void Update () {
		if (timer >= 1) {
			timer=0;
			this.transform.Find ("ClockHour").localEulerAngles = new Vector3 (0, 0, (float)((System.DateTime.Now.Hour % 12 + System.DateTime.Now.Minute/60.0) * (360.0 / 12.0)));
			this.transform.Find ("ClockMinute").localEulerAngles = new Vector3 (0, 0, (float)((System.DateTime.Now.Minute % 60) * (360.0 / 60.0)));
			this.transform.Find ("ClockSecond").localEulerAngles = new Vector3 (0, 0, (float)((System.DateTime.Now.Second % 60) * (360.0 / 60.0)));
			this.transform.Find("ClockTickSource").GetComponent<AudioSource>().Play();
		}
		timer += Time.deltaTime;
	}
}

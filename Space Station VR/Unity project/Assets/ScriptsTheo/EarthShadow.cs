using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EarthShadow : MonoBehaviour
{
    GameObject gm;

    // Start is called before the first frame update
    void Start()
    {
        gm = this.gameObject.transform.GetChild(0).gameObject;
    }

    // Update is called once per frame
    void Update()
    {
        var light = gm.GetComponent<Light>();
        light.color = new Color(-100f, -100f, -100f, 1);
    }
}

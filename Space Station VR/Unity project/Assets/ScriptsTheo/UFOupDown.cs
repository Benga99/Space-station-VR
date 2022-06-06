using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UFOupDown : MonoBehaviour
{
    float x, y, z, length;
    // Start is called before the first frame update
    void Start()
    {
        x = transform.localPosition.x;
        z = transform.localPosition.z;
        length = Random.Range(0.5f, 1.2f);
    }

    // Update is called once per frame
    void Update()
    {
        y = Mathf.PingPong(Time.time, length);
        transform.localPosition= new Vector3(x, y, z);
    }
}

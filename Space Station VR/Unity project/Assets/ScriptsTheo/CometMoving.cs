using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CometMoving : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        this.gameObject.transform.position = new Vector3(this.gameObject.transform.position.x - Time.deltaTime/5f,
                                                         this.gameObject.transform.position.y - Time.deltaTime/50f,
                                                         this.gameObject.transform.position.z);
    }
}

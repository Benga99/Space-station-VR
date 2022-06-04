using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UFOParentRotate : MonoBehaviour
{
    public int UFOsDown = 0;
    public GameObject key;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.Rotate(0, Time.deltaTime * 10, 0);
        
        if(UFOsDown == 14)
        {
            //instantiate key
            key.SetActive(true);
            //play sound

        }
    }
}

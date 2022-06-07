using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UFOParentRotate : MonoBehaviour
{
    public int UFOsDown = 0;
    public GameObject key;
    public AudioSource destroyAudio;
    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(goUp());
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

    private IEnumerator goUp()
    {
        float y = 0;
        while (y < 5)
        {
            y += Time.deltaTime;
            this.transform.position = new Vector3(transform.position.x, transform.position.y + Time.deltaTime, transform.position.z);
            yield return new WaitForEndOfFrame();
        }
    }
}

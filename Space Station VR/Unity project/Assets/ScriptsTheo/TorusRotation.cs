using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TorusRotation : MonoBehaviour
{
    [SerializeField]
    [Range(1, 10)]
    private float speed;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.Rotate(0, -Time.deltaTime * speed * 20, 0);
    }
}
